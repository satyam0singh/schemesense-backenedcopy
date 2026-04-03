import requests
import json

# Local URL for testing
URL = "http://127.0.0.1:10001/chat"

# Example Scheme Data (PM-Kisan)
pm_kisan = {
    "scheme_id": "SCH001",
    "scheme_name": "PM Kisan Samman Nidhi",
    "scheme_category": ["Agriculture", "Income Support"],
    "target_beneficiary": ["Small and Marginal Farmers"],
    "eligibility": {
        "logic_rules": [
            {"field": "occupation", "operator": "==", "value": "farmer"},
            {"field": "income", "operator": "<=", "value": 200000}
        ]
    },
    "benefits": {
        "amount": "₹6,000/year",
        "description": "Direct income support to farmers"
    },
    "documents_required": ["Aadhaar Card", "Land Records", "Bank Account"],
    "application": {
        "mode": ["Online", "CSC"],
        "link": "https://pmkisan.gov.in"
    }
}

user_profile = {
    "occupation": "farmer",
    "income": 150000
}

def test_chat(query, scheme=None, profile=None):
    payload = {
        "query": query,
        "scheme": scheme,
        "user_profile": profile
    }
    response = requests.post(URL, json=payload)
    print(f"\nQUERY: {query}")
    if response.status_code == 200:
        data = response.json()
        print(f"RESPONSE: {data['response']}")
        if data.get('related_schemes'):
            print(f"RELATED: {[s['scheme_name'] for s in data['related_schemes']]}")
    else:
        print(f"ERROR: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("--- TESTING CONTEXT-AWARE CHATBOT ---")
    
    # 1. Benefits Query
    test_chat("What are the benefits?", scheme=pm_kisan)
    
    # 2. Documents Query
    test_chat("What documents do I need?", scheme=pm_kisan)
    
    # 3. Eligibility Query (with Profile)
    test_chat("Am I eligible?", scheme=pm_kisan, profile=user_profile)
    
    # 4. Application Query
    test_chat("How to apply?", scheme=pm_kisan)
    
    # 5. General Context Query
    test_chat("Tell me more about this", scheme=pm_kisan)
