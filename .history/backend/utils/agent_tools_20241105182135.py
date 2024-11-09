import requests
import polyline
from shapely.geometry import LineString
import geopandas as gpd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

class GoogleAPIClient:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_place_info(self, address):
        """
        Get place information using Google Places API.
        """
        url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        params = {
            "input": address,
            "inputtype": "textquery",
            "fields": "formatted_address,name,business_status,geometry",
            "key": self.api_key,
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if "candidates" in data and data["candidates"]:
                logging.info(f"Place info retrieved for {address}")
                return data["candidates"][0]
            else:
                logging.warning(f"No candidates found for {address}")
                return None
        else:
            logging.error(f"Failed to get place info for {address}")
            return None

    def get_route(self, origin, destination):
        """
        Get route information between origin and destination using Google Routes API.
        """
        url = 'https://routes.googleapis.com/directions/v2:computeRoutes'
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': self.api_key,
            'X-Goog-FieldMask': 'routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline'
        }
        payload = {
            "origin": {"location": {"latLng": origin}},
            "destination": {"location": {"latLng": destination}},
            "travelMode": "TRANSIT",
            "computeAlternativeRoutes": False,
            "routeModifiers": {
                "avoidTolls": False,
                "avoidHighways": False,
                "avoidFerries": False
            },
            "languageCode": "en-US",
            "units": "IMPERIAL"
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            logging.info("Route successfully retrieved.")
            return response.json()
        else:
            logging.error("Failed to retrieve route information.")
            return None

    def visualize_route(self, route_polyline):
        """
        Decode polyline and visualize route using GeoDataFrame.
        """
        polyline_coords = polyline.decode(route_polyline)
        polyline_coords = [(lng, lat) for lat, lng in polyline_coords]
        route_line = LineString(polyline_coords)
        route_gdf = gpd.GeoDataFrame(geometry=[route_line], crs='EPSG:4326')
        return route_gdf

if __name__ == '__main__':  
    import dotenv 
    import os 
    dotenv.load_dotenv()
    # Initialize the GoogleAPIClient with the API key
    client = GoogleAPIClient(api_key=os.getenv('GOOGLE_API_KEY'))
    # Fetch locations
    home_location = client.get_place_info('Home, Stratford, London')
    work_location = client.get_place_info('Work, West Kensington, London')

    # Ensure valid location data before requesting route
    if home_location and work_location:
        logging.info(f"Home location: {home_location}")
        logging.info(f"Work location: {work_location}")
        origin = home_location['geometry']['location']
        destination = work_location['geometry']['location']
        
        # Fetch route
        routes_result = client.get_route(origin, destination)
        
        # Check and visualize route if available
        if routes_result and 'routes' in routes_result:
            client.visualize_route(routes_result['routes'][0]['polyline']['encodedPolyline'])
        else:
            logging.warning("Route not available.")
    else:
        logging.warning("Failed to retrieve one or more locations.")
