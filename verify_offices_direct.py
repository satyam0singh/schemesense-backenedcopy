from app.services.office_service import office_service

def test_service_logic(lat, lng):
    print(f"\n--- TESTING SERVICE LOGIC AT ({lat}, {lng}) ---")
    results = office_service.get_nearest_offices(lat, lng, limit=5)
    print(f"Nearest {len(results)} offices found:")
    for res in results:
        print(f"- {res['name']} ({res['type']}) | Distance: {res['distance']}km")

if __name__ == "__main__":
    # Test 1: Ghaziabad Coordinates
    test_service_logic(28.6692, 77.4538)
    
    # Test 2: Lucknow Coordinates
    test_service_logic(26.8467, 80.9462)
    
    # Test 3: Mumbai Coordinates
    test_service_logic(19.0760, 72.8777)
