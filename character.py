import json

class Character:
    def __init__(self, file_manager):
        self.file_manager = file_manager
        # Default character stats
        self.stats = {
            "health": 100,
            "strength": 10,
            "level": 1
        }
        self.load_progress()
    
    def load_progress(self):
        """Load character progress from file"""
        saved_character = self.file_manager.load_character_progress()
        if saved_character:
            self.stats = saved_character
            print("Character progress loaded successfully.")
            return True
        else:
            print("No saved character progress found.")
            return False
    
    def save_progress(self):
        """Save character progress to file"""
        self.file_manager.save_character_progress(self.stats)
    
    def level_up(self):
        """Increment character level"""
        self.stats["level"] += 1
        self.save_progress()
    
    def get_stats(self):
        """Return character stats"""
        return self.stats
