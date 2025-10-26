"""
Manages separate progress tracking for each world map.
Keeps track of:
- Completed encounters
- Unlocked areas
- Player achievements/stats per world
"""
import json
import os


class WorldProgress:
    def __init__(self):
        self.completed_encounters = set()  # IDs of completed encounters
        self.unlocked_areas = set()  # Areas that become available after completing certain encounters
        self.stats = {
            'combat_wins': 0,
            'items_collected': 0,
            'credits_earned': 0,
            'minigames_completed': 0
        }

    def to_dict(self):
        """Convert progress to a dictionary for saving."""
        return {
            'completed_encounters': list(self.completed_encounters),
            'unlocked_areas': list(self.unlocked_areas),
            'stats': self.stats
        }

    def from_dict(self, data):
        """Load progress from a dictionary."""
        self.completed_encounters = set(data.get('completed_encounters', []))
        self.unlocked_areas = set(data.get('unlocked_areas', []))
        self.stats = data.get('stats', {
            'combat_wins': 0,
            'items_collected': 0,
            'credits_earned': 0,
            'minigames_completed': 0
        })


class ProgressManager:
    _instance = None
    SAVE_DIR = 'saves'
    SAVE_FILE = 'world_progress.json'

    @classmethod
    def get_instance(cls):
        """Singleton pattern to ensure one progress manager."""
        if cls._instance is None:
            cls._instance = ProgressManager()
        return cls._instance

    def __init__(self):
        """Initialize progress tracking for each world."""
        self.worlds = {
            'world1': WorldProgress(),
            'world2': WorldProgress(),
            'world3': WorldProgress(),
            'world4': WorldProgress()
        }
        self.current_world = None
        self.load_progress()

    def set_current_world(self, world_id):
        """Set the active world for progress tracking."""
        if world_id in self.worlds:
            self.current_world = world_id
            return self.worlds[world_id]
        return None

    def get_world_progress(self, world_id):
        """Get progress for a specific world."""
        return self.worlds.get(world_id)

    def complete_encounter(self, encounter_id):
        """Mark an encounter as completed in the current world."""
        if self.current_world and encounter_id:
            self.worlds[self.current_world].completed_encounters.add(encounter_id)
            self.save_progress()

    def is_encounter_completed(self, encounter_id):
        """Check if an encounter is completed in the current world."""
        if self.current_world and encounter_id:
            return encounter_id in self.worlds[self.current_world].completed_encounters
        return False

    def update_stats(self, stat_type, value=1):
        """Update statistics for the current world."""
        if self.current_world:
            world = self.worlds[self.current_world]
            if stat_type in world.stats:
                world.stats[stat_type] += value
                self.save_progress()

    def save_progress(self):
        """Save all world progress to file."""
        try:
            os.makedirs(self.SAVE_DIR, exist_ok=True)
            save_path = os.path.join(self.SAVE_DIR, self.SAVE_FILE)
            
            # Convert progress to saveable format
            save_data = {
                world_id: progress.to_dict()
                for world_id, progress in self.worlds.items()
            }
            
            with open(save_path, 'w') as f:
                json.dump(save_data, f, indent=2)
        except Exception as e:
            print(f"Error saving progress: {e}")

    def load_progress(self):
        """Load all world progress from file."""
        try:
            save_path = os.path.join(self.SAVE_DIR, self.SAVE_FILE)
            if os.path.exists(save_path):
                with open(save_path, 'r') as f:
                    save_data = json.load(f)
                
                # Load progress for each world
                for world_id, data in save_data.items():
                    if world_id in self.worlds:
                        self.worlds[world_id].from_dict(data)
        except Exception as e:
            print(f"Error loading progress: {e}")