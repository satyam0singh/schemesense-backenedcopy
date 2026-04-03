import requests

# Local URL for testing (using port 10001 where reload is enabled)
URL = "http://127.0.0.1:10001/chat"

def test_jury_questions():
    questions = [
        "What is SchemeSense?",
        "Who built this?",
        "How it works?",
        "Tell me about space exploration", # Unrelated
        "Find me some business loans" # Valid scheme query
    ]
    
    print(f"\n--- TESTING JURY MODE ROBUSTNESS ---")
    for q in questions:
        payload = {"query": q}
        response = requests.post(URL, json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"QUERY: {q}")
            print(f"RESPONSE: {data['response']}")
            print(f"SCHEMES FOUND: {len(data.get('schemes', []))}")
            print("-" * 30)
        else:
            print(f"ERROR: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_jury_questions()
