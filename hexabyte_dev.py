from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import math 
import random # Needed for NPC movement logic

# --- 1. CORE SETUP & GLOBALS ---
window.title = "hEXabyte Dev - Voxel Sandbox"
window.borderless = True
window.size = (1600, 900) 
window.vsync = False         # CRITICAL FIX: Disable VSync to enforce the FPS limit
window.fps_limit = 15        # SET FPS LIMIT TO 15 

app = Ursina()

# --- PHYSICS REMOVAL: No physics engine initialization here ---

# Version control (keeping the user-requested version)
VERSION = "0.2711251435" 

# Day/Night Cycle Variables (Still active for aesthetic changes)
TIME_SCALE = 0.05 
current_time = 0.0

# Global lists
placed_entities = [] # User-placed (destructible, counted) entities
default_scene_entities = [] # Permanent (indestructible, not counted) entities
npcs = [] # List to hold all moving NPCs

# --- HELPER FUNCTION: Ensure Vibrant Color (No near-white) ---
VIBRANT_COLORS = [
    color.red, color.blue, color.yellow, color.magenta, color.cyan,
    color.orange, color.pink, color.lime, color.violet
]
def get_vibrant_color():
    """Selects a random, highly saturated color from a predefined list."""
    return random.choice(VIBRANT_COLORS)

# NEW: Define specific colors for the NPC head/face
SKIN_COLORS = [
    color.black, 
    color.rgb(101, 67, 33),  # Dark Brown
    color.rgb(193, 154, 107), # Light Brown
    color.yellow, 
    color.white
]

# --- 2. UI AND DIAGNOSTICS (MOVED TO TOP TO PREVENT NAMEERROR) ---

def update_diagnostics():
    """Updates the on-screen text with current state."""
    # CRITICAL FIX: Safely retrieve FPS. The time.fps attribute may not exist during the very first frames
    # when update() is called during the application startup process.
    current_fps = round(time.fps) if hasattr(time, 'fps') else 0 

    diagnostics.text = (
        f"hEXabyte V{VERSION}\n"
        f"FPS: {current_fps} / {window.fps_limit} (Target)\n" 
        f"Selected: {current_entity_name}\n"
        f"Entities: {len(placed_entities)}\n" 
        f"NPCs: {len(npcs)}\n" 
        f"Controls:\n"
        f"  LMB: Place, RMB: Destroy/Kill\n" 
        f"  PageUp/Down: Cycle Entity\n"
        f"  S: Spawn NPC\n"
        f"  ESC: Quit App"
    )

# Placeholder variables must be defined before use
current_entity_index = 0
entity_types = [
    ('Cube (Static)', None), 
    ('Sphere', None), 
    ('Plank', None) 
]
current_entity_name = entity_types[current_entity_index][0]

diagnostics = Text(
    text='',
    position=window.top_left + Vec2(0.01, -0.01),
    scale=1.5,
    background=True,
    background_color=color.rgba(0, 0, 0, 150) 
)


# --- 3. VOXEL ENTITIES (Static and Moving) ---

class VoxelCube(Entity):
    # Standard STATIC Voxel
    def __init__(self, position, **kwargs):
        super().__init__(
            model='cube',
            texture='white_cube', 
            color=get_vibrant_color(),
            collider='box',
            position=position,
            scale=(1,1,1),
            **kwargs
        )


class VoxelSphere(Entity):
    # Standard STATIC Voxel (no physics)
    def __init__(self, position, **kwargs):
        super().__init__(
            model='sphere',
            texture='white_cube',
            color=get_vibrant_color(),
            collider='sphere',       
            position=position,
            scale=(1,1,1),
            **kwargs
        )

class SeeSaw(Entity):
    # Plank (no physics, just a static elongated cube)
    def __init__(self, position, **kwargs):
        super().__init__(
            model='cube',
            texture='white_cube',
            color=get_vibrant_color().tint(-0.4), # Darker color for contrast
            collider='box',
            position=position,
            scale_x=6,
            scale_y=0.2,
            scale_z=1,
            **kwargs
        )

# Update entity_types list now that classes are defined
entity_types = [
    ('Cube (Static)', VoxelCube),
    ('Sphere', VoxelSphere), 
    ('Plank', SeeSaw) 
]
current_entity_name = entity_types[current_entity_index][0] 

class VoxelNPC(Entity):
    # NPC composed of multiple cubes to look like a person
    def __init__(self, position, **kwargs):
        # Base Entity acts as the parent for movement.
        super().__init__(
            position=position,
            speed=2.0,
            direction=Vec3(random.uniform(-1, 1), 0, random.uniform(-1, 1)).normalized(),
            turn_timer=random.uniform(2, 5),
            # Use 'box' collider on the parent for easy destruction target
            collider='box', 
            scale=(1, 1, 1), 
            color=color.clear, # Make the parent entity invisible
            name="VoxelNPC", # Give it a unique name for identification
            **kwargs
        )
        
        # --- NPC is exactly 2 units tall (2 cubes high) ---
        
        # Coloring 
        head_color = random.choice(SKIN_COLORS)
        body_color = get_vibrant_color()
        legs_color = get_vibrant_color().tint(-0.2) 

        # Head (0.5 unit tall)
        self.head = Entity(
            parent=self, 
            model='cube', 
            color=head_color, 
            position=(0, 0.75, 0), 
            scale=(1, 0.5, 1),
            name="VoxelNPC_Head" 
        ) 
        
        # Body (1.0 unit tall)
        self.body = Entity(
            parent=self, 
            model='cube', 
            color=body_color, 
            position=(0, 0.0, 0), 
            scale=(1, 1.0, 1),
            name="VoxelNPC_Body" 
        )
        
        # Legs (0.5 unit tall)
        self.legs = Entity(
            parent=self, 
            model='cube', 
            color=legs_color, 
            position=(0, -0.75, 0), 
            scale=(1, 0.5, 1),
            name="VoxelNPC_Legs"
        )
    
    def update(self):
        # Move the NPC horizontally (using the parent entity)
        self.position += self.direction * self.speed * time.dt
        
        # Simple boundary check: Reverse direction if too far out
        boundary = 45
        if abs(self.x) > boundary or abs(self.z) > boundary:
            # Reverse direction vector
            self.direction *= -1 
            self.turn_timer = random.uniform(3, 7) # Force a new turn time

        # Randomly change direction
        self.turn_timer -= time.dt
        if self.turn_timer <= 0:
            # Generate a new random direction vector (normalized)
            self.direction = Vec3(random.uniform(-1, 1), 0, random.uniform(-1, 1)).normalized()
            self.turn_timer = random.uniform(3, 7) # Reset timer


# --- 4. GROUND SETUP (Static Collider) ---
ground = Entity(
    model='plane',
    collider='box',
    scale=(100, 1, 100),
    texture='grass',
    texture_scale=(100, 100),
    color=color.green.tint(-0.2), 
    y=0 # Standard Y position
)

# --- 5. DEFAULT SCENE SETUP (Indestructible, not counted) ---
def spawn_single_npc():
    """Spawns a single Voxel NPC at a random location."""
    x = random.uniform(-15, 15)
    z = random.uniform(-15, 15)
    # The 2.0 unit tall NPC's base is at y=-1.0, so parent center must be at y=1.0.
    npc = VoxelNPC(position=(x, 1.0, z)) # Changed Y position to 1.0 for 2-unit tall NPC
    npcs.append(npc)
    # The diagnostics are updated in the main update() loop to avoid startup errors.
    return npc

def setup_default_scene():
    """Spawns initial NPCs."""
    
    print("Setting up default scene with 8 new Voxel NPCs...")
    
    # --- Spawn 8 Walking Voxel NPCs ---
    for _ in range(8):
        spawn_single_npc()
    
setup_default_scene()
# The diagnostics are updated in the main update() loop to avoid startup errors.


# --- 6. DYNAMIC LIGHTING & MUSIC ---
AmbientLight(color=color.rgba(100, 100, 100, 100))
sun = DirectionalLight(y=10, z=10, rotation=(45, 45, 0), color=color.white)
Sky() 

def update_day_night_cycle():
    """Rotates the sun and adjusts lighting and sky colors based on time."""
    global current_time
    
    current_time += time.dt * TIME_SCALE
    if current_time > 360: 
        current_time -= 360
    
    # Sun rotation (basic orbit)
    sun.x = math.sin(math.radians(current_time)) * 20
    sun.y = math.cos(math.radians(current_time)) * 20 
    sun.z = 10
    sun.rotation_x = current_time 

    # Adjusting light intensity based on sun position
    intensity = max(0.1, min(1.0, (sun.y + 10) / 20)) 
    
    # Simple color shift for day/night feel
    if sun.y > 0:
        scene.fog_color = color.light_gray
    else:
        scene.fog_color = color.black

try:
    # Use 'loop=True' for continuous background music
    Audio('assets/bouncy_tune.ogg', loop=True, autoplay=True)
except Exception:
    print("Warning: Background music 'bouncy_tune.ogg' asset not found.")

# --- 7. GHOST PREVIEW SETUP ---
ghost_object = Entity(
    model='cube', 
    color=color.rgba(200, 200, 255, 128), # Semi-transparent blue
    collider=None, # No collisions
    visible=False,
    scale=(1,1,1) 
)


# --- 8. INPUT HANDLING ---

def input(key):
    global current_entity_index, current_entity_name

    # LEFT Click: Place the entity (Adds to destructible/counted list)
    if key == 'left mouse down':
        
        if mouse.hovered_entity and mouse.normal:
            entity_name, entity_class = entity_types[current_entity_index]
            
            target_pos = mouse.world_point + mouse.normal * 0.5 
            
            position = Vec3(
                round(target_pos.x),
                round(target_pos.y),
                round(target_pos.z)
            )

            if mouse.hovered_entity != player:
                try:
                    # Place Plank slightly higher
                    if entity_name.startswith('Plank'):
                        position += Vec3(0, 0.5, 0)
                        
                    new_entity = entity_class(position=position)
                    placed_entities.append(new_entity) # Only player-placed entities here
                    print(f"Placed {entity_name} successfully at {new_entity.position}")
                    update_diagnostics() 
                except Exception as e:
                    print(f"CRITICAL VOXEL PLACEMENT ERROR (Placing {entity_name}): {e}")


    # RIGHT Click: Destroy the entity (or kill NPC)
    if key == 'right mouse down':
        hovered = mouse.hovered_entity
        npc_to_destroy = None

        # --- NPC Kill Check ---
        # 1. Check if the hovered entity is the parent NPC itself
        if hovered in npcs:
            npc_to_destroy = hovered
        # 2. Check if the hovered entity is a child part of an NPC
        elif hovered and hovered.parent and hovered.parent.name == "VoxelNPC":
            # Find the parent in the npcs list
            try:
                # We use list comprehension to safely find the parent in the tracked list
                npc_to_destroy = [n for n in npcs if n == hovered.parent][0] 
            except IndexError:
                # Safety break if parent is somehow not in the list
                pass


        if npc_to_destroy:
            # CRASH FIX: Store the name BEFORE destroying the entity.
            npc_name = npc_to_destroy.name 
            
            # Kill the NPC
            npcs.remove(npc_to_destroy)
            destroy(npc_to_destroy) # Destroying the parent entity destroys all its children
            
            print(f"Destroyed Voxel NPC: {npc_name}") # Use the stored name
            update_diagnostics()
            return # Stop here if an NPC was killed

        # --- Placed Entity Destruction Check (only runs if NPC wasn't killed) ---
        if hovered and hovered in placed_entities: 
            try:
                placed_entities.remove(hovered)
                destroy(hovered)
                print(f"Destroyed entity: {hovered.name}")
                update_diagnostics()
            except Exception as e:
                print(f"Error destroying entity: {e}")


    # PageUp / PageDown: Cycle through entities
    if key == 'page up' or key == 'page down':
        current_entity_index = (current_entity_index + (1 if key == 'page up' else -1)) % len(entity_types)
        current_entity_name = entity_types[current_entity_index][0]
        
        ghost_model_name = current_entity_name.lower().split(' ')[0]
        
        if current_entity_name.startswith('Plank'):
            ghost_object.model = 'cube'
            ghost_object.scale = (6, 0.2, 1)
        else:
            ghost_object.model = ghost_model_name if ghost_model_name in ('cube', 'sphere') else 'cube'
            ghost_object.scale = (1, 1, 1)
            
        update_diagnostics()

    # NEW: 'S' key to spawn an NPC
    if key == 's':
        spawn_single_npc()
        print("Spawned new Voxel NPC via 'S' key.")
        # Need to call diagnostics here for immediate NPC count update on 'S' press
        update_diagnostics()

    # Escape key to exit the app
    if key == 'escape':
        application.quit()


# --- 9. PLAYER AND MAIN LOOP ---

player = FirstPersonController(y=1)
player.cursor.color = color.rgba(0,0,0,128) 

def update():
    """Called every frame."""
    update_day_night_cycle()
    
    # GHOST OBJECT VISUALIZATION
    if mouse.hovered_entity and mouse.normal and mouse.hovered_entity != player:
        ghost_object.visible = True
        
        target_pos = mouse.world_point + mouse.normal * 0.5
        
        position = Vec3(
            round(target_pos.x),
            round(target_pos.y),
            round(target_pos.z)
        )
        
        if current_entity_name.startswith('Plank'):
             position += Vec3(0, 0.5, 0)

        ghost_object.position = position
    else:
        ghost_object.visible = False
        
    # Always update diagnostics to show current FPS
    update_diagnostics()


# --- RUN THE APP ---
app.run()
