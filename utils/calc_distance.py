from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from typing import Dict, Optional, List
import yaml
from pathlib import Path

class FindDistance:
    """
    A class to find distances between addresses and locate the closest supermarket.
    
    This class uses geopy to geocode addresses and calculate distances between
    predefined supermarket locations in Joinville, SC, Brazil.
    """
    def __init__(self, user_agent: str = "brazil_distance_calculator"):
        """
        Initialize the FindDistance class.
        
        Args:
            user_agent: User agent string for the Nominatim geocoder
        """
        self.geolocator = Nominatim(user_agent=user_agent)
        self.supermarkets = self._load_supermarkets()
    
    def _load_supermarkets(self) -> List[Dict[str, str]]:
        """
        Load supermarket data from YAML config file.
        
        Returns:
            List of supermarket dictionaries with name and address
        """
        config_path = Path(__file__).parent / "supermarkets.yaml"
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                return config['supermarkets']
        except FileNotFoundError:
            raise FileNotFoundError(f"Supermarkets config file not found: {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration: {e}")

    def _calculate_distance(self, address1: str, address2: str) -> Optional[float]:
        """
        Calculate the distance between two addresses in kilometers.
        
        Args:
            address1: First address as string
            address2: Second address as string
            
        Returns:
            Distance in kilometers, or None if geocoding fails
        """
        try:
            location1 = self.geolocator.geocode(address1)
            location2 = self.geolocator.geocode(address2)
        
            if not location1 or not location2:
                return None
        
            coords1 = (location1.latitude, location1.longitude)
            coords2 = (location2.latitude, location2.longitude)
            distance = geodesic(coords1, coords2)
            
            return distance.kilometers
        except Exception:
            return None

    def find_closest_supermarket(self, user_address: str) -> Optional[Dict[str, str]]:
        """
        Find the closest supermarket to a given address.
        
        Args:
            user_address: The user's address as a string
            
        Returns:
            Dict with closest supermarket name, address and distance in km,
            or None if no supermarket found or address invalid
        """
        if not user_address or not user_address.strip():
            return None

        try:
            user_location = self.geolocator.geocode(user_address)
            if not user_location:
                return None
        except Exception:
            return None
            
        closest_supermarket = None
        min_distance = float('inf')
        
        for supermarket in self.supermarkets:
            distance = self._calculate_distance(user_address, supermarket["address"])
            if distance and distance < min_distance:
                min_distance = distance
                closest_supermarket = {
                    "name": supermarket["name"],
                    "address": supermarket["address"],
                    "distance_km": round(distance, 2)
                }
        
        return closest_supermarket
