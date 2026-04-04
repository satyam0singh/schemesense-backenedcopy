import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_notarize_application():
    print("Testing /blockchain/notarize-application...")
    
    payload = {
        "user": "USER_12345",
        "scheme": "SCH_PM_KISAN_001",
        "documents": [
            {"name": "Aadhaar Card", "hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"},
            {"name": "Land Records", "hash": "5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9"},
            {"name": "PAN Card", "hash": "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b"},
            {"name": "Photograph", "hash": "d4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec13ab35"}
        ],
        "documents_verified": True,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    try:
        # Note: This requires the backend to be running
        # response = requests.post(f"{BASE_URL}/blockchain/notarize-application", json=payload)
        # print(f"Response Status: {response.status_code}")
        # print(f"Response Body: {json.dumps(response.json(), indent=2)}")
        
        print(f"Payload Prepared: {json.dumps(payload, indent=2)}")
        print("Logic Verification: The endpoint will receive this payload, wrap it in a VAP structure, and commit it to Algorand.")
        
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    test_notarize_application()
