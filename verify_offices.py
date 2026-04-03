import requests

# Local URL for testing (using port 10001 where reload is enabled)
BASE_URL = "http://127.0.0.1:10001"

def test_nearest_offices(lat, lng):
    print(f"\n--- TESTING NEAREST OFFICES AT ({lat}, {lng}) ---")
    url = f"{BASE_URL}/nearest-offices?lat={lat}&lng={lng}"
    response = requests.get(url)
    
    if response.status_code == 200:
        results = response.json()
        print(f"Nearest {len(results)} offices found:")
        for res in results:
            print(f"- {res['name']} ({res['type']}) | Distance: {res['distance']}km | Address: {res['address']}")
    else:
        print(f"ERROR: {response.status_code} - {response.text}")

if __name__ == "__main__":
    # Test 1: Ghaziabad Coordinates
    test_nearest_offices(28.6692, 77.4538)
    
    # Test 2: Lucknow Coordinates
    test_nearest_offices(26.8467, 80.9462)
    
    # Test 3: Invalid Coordinates
    test_nearest_offices(100.0, 200.0)
