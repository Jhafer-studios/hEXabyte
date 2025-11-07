# -*- coding: utf-8 -*-
from ursina import *
# CRITICAL FIX: Explicitly import the FirstPersonController class
from ursina.prefabs.first_person_controller import FirstPersonController

# --- Engine Configuration & Global State ---

# Global list to track all placed entities (used for counter and deletion)
scene_entities = []

# Global dictionary for engine settings
SETTINGS = {
    'mvmtspd': 8.0,
    'skyclr': color.rgb(150, 200, 255),
}

# NEW: Object placement state
# Placement objects are now only Cube and Sphere
placement_objects = ['cube', 'sphere']
current_object_index = 0
ghost_object = None # This will be our preview
diagnostic_text = None # This will hold our stats

# --- Core Engine Functions (Shape Placement) ---

def add_shape(model_name='cube', pos=(0,1,0), rot=(0,0,0), scl=(1,1,1), clr=color.orange):
    """Adds a new primitive shape to the scene and tracks it."""
    print(f"Adding shape: {model_name}")
    
    # Use the correct collider for primitive shapes
    collider_type = 'box' if model_name == 'cube' else 'sphere'
    
    e = Entity(
        model=model_name,
        collider=collider_type,
        position=pos,
        rotation=rot,
        scale=scl,
        color=clr
    )
    
    scene_entities.append(e)
    print(f"Entity {e.name} added to scene_entities.")
    return e


# --- Configuration ---
app = Ursina(
    title='hEXabyte Dev 0.1511251740 (Core Sandbox)',
    # FIX: Fullscreen is set to True. The 'size' parameter is removed 
    # to allow the engine to use the monitor's native resolution when fullscreen is active.
    fullscreen=True,
    borderless=False,
    development_mode=True # EXPLICITLY enable dev mode
)
window.exit_button.visible = False # Hide the default exit button
window.fps_counter.enabled = False 

# FIX: Move console to F8 (with safety check)
if hasattr(window, 'console') and window.console:
    window.console.hotkey = 'f8'
else:
    print("WARNING: Could not find window.console. Dev console (F8) may be unavailable.")

# --- Utility Functions ---

def input(key):
    """Custom input handler for game controls."""
    global current_object_index, ghost_object
    
    if key == 'escape':
        # Safely exit the application
        print("Exiting application...")
        application.quit()
    
    # --- Object Placement Controls ---
    if key == 'page up':
        # Cycle forward (only two objects now)
        current_object_index = (current_object_index + 1) % len(placement_objects)
        ghost_object.model = placement_objects[current_object_index]
    
    if key == 'page down':
        # Cycle backward
        current_object_index = (current_object_index - 1) % len(placement_objects)
        ghost_object.model = placement_objects[current_object_index]
    
    if key == 'left mouse down':
        # Place object if hovering over a valid entity
        if mouse.hovered_entity and mouse.normal:
            pos = mouse.world_point + mouse.normal * 0.5 # Place *on* the surface
            add_shape(
                model_name=placement_objects[current_object_index], 
                pos=pos,
                clr=color.random_color() # Add some variety
            )
            
    if key == 'right mouse down':
        # Delete object if it's in our scene_entities list
        if mouse.hovered_entity and mouse.hovered_entity in scene_entities:
            print(f"Destroying: {mouse.hovered_entity.name}")
            scene_entities.remove(mouse.hovered_entity)
            destroy(mouse.hovered_entity)


def update():
    """Game logic update loop."""
    global diagnostic_text
    
    # --- Ghost Object Placement ---
    if mouse.hovered_entity:
        # Project ghost object onto the surface
        ghost_object.visible = True
        ghost_object.position = mouse.world_point + mouse.normal * 0.5
        
        # Ensure ghost rotation matches the surface normal for a nice placement preview
        ghost_object.rotation = Vec3(0, 0, 0) # Reset rotation
        
    else:
        # Hide ghost object if not pointing at anything
        ghost_object.visible = False

    # --- Diagnostics Text ---
    if diagnostic_text:
        pos = player.position
        
        diag_string = f"""
Version: 0.1511251740
Coords: (X: {pos.x:.1f}, Y: {pos.y:.1f}, Z: {pos.z:.1f})
Objects: {len(scene_entities)}
Selected: {placement_objects[current_object_index].upper()}
"""
        diagnostic_text.text = diag_string

    # Check if the player is too low (e.g., fell off the world)
    if player.y < -10:
        print("Player fell out of bounds. Resetting position.")
        player.y = 5
        player.x = 0
        player.z = 0

# --- Game World Setup (Editor Environment) ---

# Skybox (a simple solid color is efficient)
Sky(color=SETTINGS['skyclr']) # Use setting

# Create a simple ground plane (required for player collisions)
ground = Entity(
    model='plane',
    collider='box',
    scale=(100, 1, 100),
    texture='white_cube',
    texture_scale=(100, 100),
    color=color.rgb(100, 100, 100)
)

# --- NEW: Setup Ghost Object ---
ghost_object = Entity(
    model=placement_objects[current_object_index],
    color=color.rgba(200, 200, 255, 128), # Semi-transparent blue
    collider=None, # No collisions
    visible=False
)

# --- NEW: Setup Diagnostics Text ---
diagnostic_text = Text(
    origin=(-.5, .5), # Top-left origin
    position=window.top_left,
    text="",
    background=True,
    background_color=color.rgba(0,0,0,128)
)


# --- Player Controller ---
player = FirstPersonController(
    speed=SETTINGS['mvmtspd'], # Use setting
    jump_height=1.5,
    gravity=0.8,
)
player.position = (0, 2, 0) 
player.cursor.color = color.rgba(0,0,0,128) # Simple crosshair

# --- Console Message and Final Run ---
print("\n--- hEXabyte Dev Loaded (Core Sandbox Mode) ---")
print("Controls: WASD to move, Space to jump, Mouse to look, ESC to quit.")
print("--- EDITOR CONTROLS ---")
print("  F10: Toggle Wireframe")
print("  F8: Open Developer Console (Use this to input direct commands!)")
print("  PageUp/PageDown: Cycle Object (Cube, Sphere)")
print("  Left Click: Place Object")
print("  Right Click: Delete Placed Object")

# Start the application loop
app.run()
