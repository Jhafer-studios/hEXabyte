# hEXabyte Dev - Voxel Sandbox Project
hEXabyte is a sandbox project developed using the Ursina Engine (a Python-based wrapper for the Panda3D game engine). The core philosophy is to maintain extremely low technical requirements and computational overhead while exploring procedural and dynamic scene behaviors.

The game features first-person controls for navigation, real-time object placement and destruction, and dynamic scene elements like a day/night cycle and mobile Voxel NPCs.

Core Mechanics & Controls:

LMB: Place selected entity (Voxel, Sphere, Plank).

RMB: Destroy hovered entity or kill NPC.

Page Up/Down: Cycle through available placement entities.

S: Spawn a new Voxel NPC.

ESC: Quit application.

Hardware Note (V0.2+):

The game's FPS limit is currently non-functional due to VSync constraints (window.vsync = False). This means the game runs uncapped, and performance is directly determined by the host machine's CPU/GPU speed. Performance will be better on dual-core machines or newer.
