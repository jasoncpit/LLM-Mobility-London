import aiohttp
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

    def convert_to_list_coords(self, lines):
        polyline_coords = polyline.decode(lines)
        polyline_coords = [[lng, lat] for lat, lng in polyline_coords]
        return polyline_coords

    def get_route_line(self, origin_poi, destination_poi, travel_mode):
        """Get route line between two POIs using specified travel mode."""
        mode = 'WALK' if travel_mode == 'NONE' else travel_mode
        route = self.get_route(origin_poi, destination_poi, mode)
        
        # Check if we have a valid route with actual points
        lines = route['routes'][0]['polyline']['encodedPolyline']
        return self.convert_to_list_coords(lines)

    def convert_time_to_timestamp(self, time):
        return int(time.split(':')[0]) * 60 + int(time.split(':')[1])

    def compute_routes(self, traces):
        from concurrent.futures import ThreadPoolExecutor
        import functools
        
        # Create a list of all route requests upfront
        route_requests = []
        time = [] 
        day = []
        for index, plan in enumerate(traces[-1]['plans']):
            entries = plan.entries
            for origin, destination in zip(entries[:-1], entries[1:]):
                route_requests.append((
                    origin.poi_output,
                    destination.poi_output,
                    origin.travel_mode.value
                ))
            for entry in entries:
                # Skip the first entry as it is the home location
                time.append(self.convert_time_to_timestamp(entry.time))[1:]
                day.append(index)[1:]

        # Define worker function
        def fetch_route(args):
            origin, destination, mode = args
            try:
                return self.get_route_line(origin, destination, mode)
            except Exception as e:
                logging.error(f"Error fetching route: {e}")
                return None
        
        # Use ThreadPoolExecutor to fetch routes in parallel
        with ThreadPoolExecutor(max_workers=10) as executor:
            routes = list(executor.map(fetch_route, route_requests))
        
        return routes, time, day

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
