import requests

URL = "http://127.0.0.1:10001/chat"

def test_faq():
    print("\n--- TESTING PLATFORM FAQ ---")
    queries = ["What is SchemeSense?", "How it works?", "Who built this?"]
    for q in queries:
        payload = {"query": q}
        response = requests.post(URL, json=payload)
        if response.status_code == 200:
            print(f"Query: {q}\nResponse: {response.json()['response']}\n")
        else:
            print(f"Error {q}: {response.status_code}")

def test_jury_mode():
    print("\n--- TESTING JURY MODE (LOW CONFIDENCE) ---")
    # A query that should have low confidence for the current dataset
    payload = {"query": "How to bake a cake?"}
    response = requests.post(URL, json=payload)
    if response.status_code == 200:
        print(f"Query: {payload['query']}\nResponse: {response.json()['response']}\n")
    else:
        print(f"Error Jury: {response.status_code}")

if __name__ == "__main__":
    test_faq()
    test_jury_mode()
