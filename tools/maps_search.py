"""Google Maps search tool using SerpAPI"""
from typing import List, Dict, Optional
from serpapi import GoogleSearch
from config import settings
import time

class GoogleMapsSearchTool:
    """
    Search for local businesses on Google Maps
    Returns: name, address, phone, website, rating, reviews
    """
    
    def __init__(self):
        self.api_key = settings.serpapi_key
        if not self.api_key:
            raise ValueError("SERPAPI_KEY not found in environment variables")
    
    def search(
        self, 
        query: str, 
        location: Optional[str] = None,
        max_results: int = 20
    ) -> List[Dict]:
        """
        Search Google Maps for local businesses
        
        Args:
            query: Search query (e.g., "gyms", "Italian restaurants")
            location: Location filter (e.g., "Austin, TX")
            max_results: Maximum number of results to return
        
        Returns:
            List of business dictionaries
        """
        
        # Build search query
        full_query = query
        if location:
            full_query = f"{query} in {location}"
        
        params = {
            "engine": "google_maps",
            "q": full_query,
            "api_key": self.api_key,
            "num": min(max_results, 20)  # SerpAPI max per request
        }
        
        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            
            businesses = []
            
            if "local_results" in results:
                for result in results["local_results"][:max_results]:
                    business = {
                        "name": result.get("title", ""),
                        "address": result.get("address", ""),
                        "phone": result.get("phone", None),
                        "website": result.get("website", None),
                        "rating": result.get("rating", None),
                        "reviews": result.get("reviews", 0),
                        "type": result.get("type", ""),
                        "place_id": result.get("place_id", ""),
                        "source_url": result.get("link", ""),
                        "latitude": result.get("gps_coordinates", {}).get("latitude"),
                        "longitude": result.get("gps_coordinates", {}).get("longitude"),
                    }
                    businesses.append(business)
            
            return businesses
            
        except Exception as e:
            print(f"Error searching Google Maps: {e}")
            return []
    
    def has_website(self, business: Dict) -> bool:
        """Check if a business has a website"""
        website = business.get("website")
        return website is not None and website != "" and website != "N/A"

# Singleton instance
maps_search_tool = GoogleMapsSearchTool() if settings.serpapi_key else None
