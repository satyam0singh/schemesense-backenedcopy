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
            {"name": "BDO Office North Bangalore", "type": "BDO", "lat": 13.0358, "lng": 77.5970, "address": "Hebbal, Bangalore"},
            
            # Final Authorities (SDM / District Collectorate)
            {"name": "SDM Office Ghaziabad", "type": "Final Authority", "lat": 28.6690, "lng": 77.4230, "address": "Collectorate, Ghaziabad"},
            {"name": "District Collectorate Lucknow", "type": "Final Authority", "lat": 26.8588, "lng": 80.9400, "address": "Lucknow DM Office"},
            {"name": "SDM Mehrauli Office", "type": "Final Authority", "lat": 28.5140, "lng": 77.1850, "address": "Mehrauli District Center"},
            {"name": "Pune Collectorate", "type": "Final Authority", "lat": 18.5284, "lng": 73.8739, "address": "Pune Station Road"},
            {"name": "Bangalore Urban DC Office", "type": "Final Authority", "lat": 12.9779, "lng": 77.5852, "address": "Kandaya Bhavan, Bangalore"}
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

    def get_best_help_path(self, user_lat: float, user_lng: float) -> List[Dict[str, Any]]:
        """
        Creates a logical 3-step sequence: CSC -> BDO -> Final Authority.
        """
        # Step 1: Nearest CSC
        cscs = [o for o in self.get_nearest_offices(user_lat, user_lng, limit=50) if o["type"] == "CSC"]
        best_csc = cscs[0] if cscs else None

        # Step 2: Nearest BDO
        bdos = [o for o in self.get_nearest_offices(user_lat, user_lng, limit=50) if o["type"] == "BDO"]
        best_bdo = bdos[0] if bdos else None

        # Step 3: Nearest Final Authority
        authorities = [o for o in self.get_nearest_offices(user_lat, user_lng, limit=50) if o["type"] == "Final Authority"]
        best_authority = authorities[0] if authorities else None

        path = []
        if best_csc: path.append(best_csc)
        if best_bdo: path.append(best_bdo)
        if best_authority: path.append(best_authority)

        return path

office_service = OfficeService()
