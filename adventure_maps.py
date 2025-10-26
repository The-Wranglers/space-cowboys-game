"""
Adventure maps configuration with normalized positions for encounters.
Each map has:
- background image path
- list of encounters with:
  - position (normalized using ui_scaling.py)
  - encounter type
  - difficulty level
  - any special parameters
"""
import os
import pygame
from utils.ui_scaling import normalize_point, normalize_radius, get_ref_size

# Constants
MAPS_DIR = os.path.join('assets', 'images', 'maps')

# Map definitions with encounters
WORLD_MAPS = {
    'world1': {
        'bg_image': os.path.join(MAPS_DIR, 'World1Map.png'),
        'encounters': [
            {
                'pos': pygame.Vector2(200, 150),  # Will be normalized on load
                'type': 'combat',
                'difficulty': 1,
                'radius': 20,
                'name': 'Space Pirates',
                'description': 'A band of space pirates blocks your path!'
            },
            {
                'pos': pygame.Vector2(400, 300),
                'type': 'shop',
                'radius': 25,
                'name': 'Trading Post',
                'description': 'A friendly merchant offers to trade with you.'
            },
            {
                'pos': pygame.Vector2(600, 200),
                'type': 'combat',
                'difficulty': 2,
                'radius': 20,
                'name': 'Alien Patrol',
                'description': 'An alien patrol ship approaches!'
            }
        ]
    },
    'world2': {
        'bg_image': os.path.join(MAPS_DIR, 'World2Map.png'),
        'encounters': [
            {
                'pos': pygame.Vector2(300, 200),
                'type': 'minigame',
                'radius': 25,
                'name': 'Asteroid Field',
                'description': 'Navigate through a dangerous asteroid field!'
            },
            {
                'pos': pygame.Vector2(500, 400),
                'type': 'combat',
                'difficulty': 3,
                'radius': 20,
                'name': 'Space Station Guards',
                'description': 'The station guards look hostile!'
            }
        ]
    },
    'world3': {
        'bg_image': os.path.join(MAPS_DIR, 'World3Map.png'),
        'encounters': [
            {
                'pos': pygame.Vector2(250, 350),
                'type': 'shop',
                'radius': 25,
                'name': 'Black Market',
                'description': 'A hidden black market dealer waves you over.'
            },
            {
                'pos': pygame.Vector2(450, 200),
                'type': 'combat',
                'difficulty': 4,
                'radius': 20,
                'name': 'Elite Guards',
                'description': 'Elite guards protect this area!'
            },
            {
                'pos': pygame.Vector2(600, 500),
                'type': 'minigame',
                'radius': 25,
                'name': 'Hacking Challenge',
                'description': 'Try to hack into the security system.'
            }
        ]
    },
    'world4': {
        'bg_image': os.path.join(MAPS_DIR, 'World4Map.png'),
        'encounters': [
            {
                'pos': pygame.Vector2(350, 250),
                'type': 'combat',
                'difficulty': 5,
                'radius': 20,
                'name': 'Boss Battle',
                'description': 'The final challenge awaits!'
            },
            {
                'pos': pygame.Vector2(200, 400),
                'type': 'shop',
                'radius': 25,
                'name': 'Supreme Weapons',
                'description': 'The ultimate weapon shop.'
            },
            {
                'pos': pygame.Vector2(500, 300),
                'type': 'minigame',
                'radius': 25,
                'name': 'Energy Core',
                'description': 'Stabilize the energy core before it explodes!'
            }
        ]
    }
}


def normalize_map_encounters(map_data):
    """
    Normalize encounter positions and radii for a map using the background image size as reference.
    This ensures encounters stay in the right relative positions when the window is resized.
    """
    try:
        # Load background image to get reference size
        bg_image = pygame.image.load(map_data['bg_image'])
        ref_size = get_ref_size(bg_image, None)
        
        # Normalize each encounter's position and radius
        for enc in map_data['encounters']:
            pos = enc['pos']
            enc['_pos_norm'] = normalize_point(pos.x, pos.y, ref_size)
            if 'radius' in enc:
                enc['_radius_norm'] = normalize_radius(enc['radius'], ref_size)
    except Exception as e:
        print(f"Error normalizing map encounters: {e}")


def init_maps():
    """
    Initialize all maps by normalizing their encounter positions.
    Call this once when loading the game.
    """
    for map_data in WORLD_MAPS.values():
        normalize_map_encounters(map_data)