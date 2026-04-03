import math
from typing import List, Dict, Any

class OfficeService:
    def __init__(self):
        # Mock Dataset for Hackathon (India-centric)
        self.offices = [
            # Delhi / Ghaziabad
            {"name": "CSC Center Ghaziabad", "type": "CSC", "lat": 28.6692, "lng": 77.4538, "address": "Navyug Market, Ghaziabad"},
            {"name": "BDO Office Loni", "type": "BDO", "lat": 28.7490, "lng": 77.2889, "address": "Loni Road, Ghaziabad"},
            {"name": "Aadhar Seva Kendra Delhi", "type": "CSC", "lat": 28.6273, "lng": 77.2153, "address": "Connaught Place, New Delhi"},
            {"name": "BDO Office Mehrauli", "type": "BDO", "lat": 28.5190, "lng": 77.1830, "address": "Mehrauli, Delhi"},
            
            # Uttar Pradesh
            {"name": "CSC Center Lucknow", "type": "CSC", "lat": 26.8467, "lng": 80.9462, "address": "Hazratganj, Lucknow"},
            {"name": "BDO Office Mohanlalganj", "type": "BDO", "lat": 26.6833, "lng": 80.9928, "address": "Mohanlalganj, UP"},
            {"name": "UP IT Solutions Hub", "type": "CSC", "lat": 28.5355, "lng": 77.3910, "address": "Sector 62, Noida"},
            
            # Maharashtra
            {"name": "CSC Center Mumbai West", "type": "CSC", "lat": 19.0760, "lng": 72.8777, "address": "Andheri West, Mumbai"},
            {"name": "BDO Office Pune City", "type": "BDO", "lat": 18.5204, "lng": 73.8567, "address": "Shivaji Nagar, Pune"},
            
            # Karnataka
            {"name": "Bangalore One Center", "type": "CSC", "lat": 12.9716, "lng": 77.5946, "address": "MG Road, Bangalore"},
            {"name": "BDO Office North Bangalore", "type": "BDO", "lat": 13.0358, "lng": 77.5970, "address": "Hebbal, Bangalore"}
        ]

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Simple Euclidean distance formula (approximation) for short local distances.
        sqrt((lat2-lat1)^2 + (lng2-lng1)^2)
        Multiply by 111 to convert degree difference to approximate KM.
        """
        dist = math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)
        # Approximate conversion: 1 degree latitude is ~111km
        return round(dist * 111, 2)

    def get_nearest_offices(self, user_lat: float, user_lng: float, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Finds and returns the top-N nearest offices sorted by distance.
        """
        results = []
        for office in self.offices:
            office_dist = self.calculate_distance(user_lat, user_lng, office["lat"], office["lng"])
            # Create a copy to avoid mutating the original dataset
            office_entry = office.copy()
            office_entry["distance"] = office_dist
            results.append(office_entry)
        
        # Sort by distance (ascending)
        sorted_results = sorted(results, key=lambda x: x["distance"])
        
        return sorted_results[:limit]

office_service = OfficeService()
