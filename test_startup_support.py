import requests
import json

# Local URL for testing (using port 10001 where reload is enabled)
URL = "http://127.0.0.1:10001/get-schemes"
CHAT_URL = "http://127.0.0.1:10001/chat"

def test_recommendation_startup():
    payload = {
        "occupation": "entrepreneur",
        "state": "Uttar Pradesh",
        "startup_stage": "prototype",
        "startup_recognition": "DPIIT Registered"
    }
    print(f"\n--- TESTING STARTUP RECOMMENDATION ---")
    response = requests.post(URL, json=payload)
    if response.status_code == 200:
        results = response.json()
        print(f"Matched {len(results)} schemes.")
        for res in results[:3]:
            print(f"- {res['scheme_name']} (Match: {res['match_type']}, Reason: {res['match_reason']})")
    else:
        print(f"ERROR: {response.status_code} - {response.text}")

def test_chat_startup():
    payload = {
        "query": "Tell me about startup grants in UP",
        "user_profile": {
            "occupation": "entrepreneur",
            "state": "Uttar Pradesh"
        }
    }
    print(f"\n--- TESTING STARTUP CHAT DISCOVERY ---")
    response = requests.post(CHAT_URL, json=payload)
    if response.status_code == 200:
        data = response.json()
        print(f"RESPONSE: {data['response']}")
        if data.get('schemes'):
            print(f"FOUND SCHEMES: {[s['scheme_name'] for s in data['schemes']]}")
    else:
        print(f"ERROR: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_recommendation_startup()
    test_chat_startup()
