import requests

# Local URL for testing (using port 10001 where reload is enabled)
URL = "http://127.0.0.1:10001/chat"

def test_expanded_faq():
    questions = [
        "How to apply?",
        "Are there any fees?",
        "Is Aadhaar mandatory?",
        "Are there schemes for women?",
        "Can I apply for multiple schemes?",
        "Tell me about student scholarships"
    ]
    
    print(f"\n--- TESTING EXPANDED JURY FAQ ---")
    for q in questions:
        payload = {"query": q}
        response = requests.post(URL, json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"QUERY: {q}")
            print(f"RESPONSE: {data['response']}")
            print("-" * 30)
        else:
            print(f"ERROR: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_expanded_faq()
