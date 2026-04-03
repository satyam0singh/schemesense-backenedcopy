import json
import os

def load_schemes():
    try:
        # Assuming schemes_master.json is in backend/
        filepath = os.path.join(os.path.dirname(__file__), "..", "schemes_master.json")
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Fallback to mock dataset
        return [
            {"name": "PM Kisan", "eligibility": "Farmer"},
            {"name": "Mudra Yojana", "eligibility": "Small Business Owner"},
            {"name": "Startup India Seed Fund", "eligibility": "Startup Founder"}
        ]
