import requests
import polyline
from shapely.geometry import LineString
import geopandas as gpd
import logging
import os 
import sys  
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from model.output_classes import POI
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
                data = data["candidates"][0]
                poi = POI(name=data["name"], latitude=data["geometry"]["location"]["lat"], longitude=data["geometry"]["location"]["lng"], address=data["formatted_address"])
                return poi
            else:
                logging.warning(f"No candidates found for {address}")
                return None
        else:
            logging.error(f"Failed to get place info for {address}")
            return None

    def get_route(self, origin:POI, destination:POI,travel_mode:str):
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
            "origin": {"location": {"latLng": {
                    "latitude": origin.latitude,
                    "longitude": origin.longitude
                }}},
            "destination": {"location": {"latLng": {
                    "latitude": destination.latitude,
                    "longitude": destination.longitude
                }}},
            "travelMode": travel_mode,
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

    def convert_polyline_to_gdf(self, route_polyline):
        """
        Decode polyline and visualize route using GeoDataFrame.
        """
        polyline_coords = polyline.decode(route_polyline)
        polyline_coords = [(lng, lat) for lat, lng in polyline_coords]
        route_line = LineString(polyline_coords)
        return route_line
        
    def compute_daily_routes(self, daily_plan):
    """
    Compute routes between consecutive locations in a daily plan where travel is involved.
    Returns a list of LineString objects representing the routes.
    """
    routes = []
    entries = daily_plan.entries
    
    for i in range(len(entries)-1):
        current = entries[i]
        next_entry = entries[i+1]
        
        # Skip if:
        # 1. No travel between locations (NONE travel mode)
        # 2. Missing POI information
        # 3. Same location (comparing coordinates)
        # 4. Same POI name
        if (current.travel_mode == 'NONE' or 
            current.poi_output is None or 
            next_entry.poi_output is None or
            current.poi_output.name == next_entry.poi_output.name or
            (current.poi_output.latitude == next_entry.poi_output.latitude and 
             current.poi_output.longitude == next_entry.poi_output.longitude)):
            continue
            
        route_result = self.get_route(
            current.poi_output,
            next_entry.poi_output,
            current.travel_mode.value if hasattr(current.travel_mode, 'value') else current.travel_mode
        )
        
        if route_result and 'routes' in route_result:
            route_line = self.convert_polyline_to_gdf(
                route_result['routes'][0]['polyline']['encodedPolyline']
            )
            routes.append({
                'from_time': current.time,
                'to_time': next_entry.time,
                'from_location': current.poi_output.name,
                'to_location': next_entry.poi_output.name,
                'travel_mode': current.travel_mode,
                'geometry': route_line
            })
        else:
            logging.warning(f"Could not compute route from {current.poi_output.name} to {next_entry.poi_output.name}")
            
        return routes

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
        # Fetch route
        routes_result = client.get_route(home_location, work_location)
        
        # Check and visualize route if available
        if routes_result and 'routes' in routes_result:
            route_line = client.convert_polyline_to_gdf(routes_result['routes'][0]['polyline']['encodedPolyline'])
            logging.info(f"Route line: {route_line}")
        else:
            logging.warning("Route not available.")
    else:
        logging.warning("Failed to retrieve one or more locations.")
