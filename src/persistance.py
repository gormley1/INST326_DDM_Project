# Create: src/persistence.py

import json
from pathlib import Path
from typing import Dict, Any

class GrocerySystemState:
    """Handles saving and loading complete system state"""
    
    def __init__(self, save_dir: Path = Path("data/saved_states")):
        self.save_dir = save_dir
        self.save_dir.mkdir(parents=True, exist_ok=True)
    
    def save_shopping_list(self, shopping_list: Dict, filename: str) -> bool:
        """Save a shopping list to JSON file"""
        filepath = self.save_dir / f"{filename}.json"
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(shopping_list, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving: {e}")
            return False
    
    def load_shopping_list(self, filename: str) -> Dict:
        """Load a shopping list from JSON file"""
        filepath = self.save_dir / f"{filename}.json"
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"File not found: {filepath}")
            return {}
        except json.JSONDecodeError:
            print(f"Invalid JSON in: {filepath}")
            return {}
    