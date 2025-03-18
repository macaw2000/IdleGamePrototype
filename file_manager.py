import os
import json

class FileManager:
    def __init__(self, save_dir):
        """Initialize the FileManager with a directory for saving files."""
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)

    def save_character_progress(self, character):
        """Save character progress to a file."""
        save_path = os.path.join(self.save_dir, "character.json")
        with open(save_path, "w") as save_file:
            json.dump(character, save_file, indent=4)
        print(f"Character progress saved to {save_path}")

    def load_character_progress(self):
        """Load character progress from a file."""
        save_path = os.path.join(self.save_dir, "character.json")
        if os.path.exists(save_path):
            with open(save_path, "r") as save_file:
                return json.load(save_file)
        return None
