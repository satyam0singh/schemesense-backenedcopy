import json
import os

class DataLoader:
    def __init__(self, filepath="schemes_master.json"):
        self.filepath = filepath
        self.schemes = []

    def _validate_scheme(self, s):
        """Mandatory crash guard"""
        required_fields = ["scheme_name", "eligibility", "ai_fields", "benefits"]
        for field in required_fields:
            if field not in s:
                return False
        return True

    def load_data(self):
        if not os.path.exists(self.filepath):
            print(f"Warning: Dataset file not found at {self.filepath}")
            return []
            
        with open(self.filepath, "r", encoding="utf-8") as file:
            try:
                raw_schemes = json.load(file)
                self.schemes = [s for s in raw_schemes if self._validate_scheme(s)]
                print(f"Loaded {len(self.schemes)} valid schemes from database out of {len(raw_schemes)}.")
            except json.JSONDecodeError:
                print("Error: Could not decode JSON dataset.")
                self.schemes = []
                
        return self.schemes

loader = DataLoader()
