from langgraph.graph import Graph 
import os
import dotenv
from langgraph.graph import END, START, StateGraph 
from nodes import Nodes
from edges import Edges
from graphstate import WeeklyPlannerState 
from langchain_openai import ChatOpenAI
from typing import List, Dict, Any, Tuple, Optional
import pandas as pd
import pydeck as pdk
from enum import Enum

dotenv.load_dotenv()


class TripColors(Enum):
    BLUE = [65, 182, 196]
    RED = [255, 0, 0]
    GREEN = [0, 255, 0]
    YELLOW = [255, 255, 0]
    PURPLE = [128, 0, 128]


def create_mobility_visualization(
    routes: List[List[List[float]]],
    time: List[int],
    day: List[int],
    travel_mode: List[str],
    schedule_df: pd.DataFrame,
    trip_color: TripColors = TripColors.BLUE,
    zoom: int = 11
) -> pdk.Deck:
    """
    Create an interactive mobility visualization using PyDeck.
    
    Args:
        routes: List of route coordinates
        time: List of timestamps
        day: List of day indices
        travel_mode: List of transportation modes
        schedule_df: DataFrame containing schedule information
        trip_color: Color for the trip paths (from TripColors enum)
        center_lat: Center latitude for the view
        center_lon: Center longitude for the view
        zoom: Initial zoom level
    
    Returns:
        pdk.Deck: PyDeck visualization object
    """
    # Create routes dataframe
    df = pd.DataFrame({
        'coordinates': routes,
        'time': time,
        'day': day,
        'travel_mode': travel_mode
    })

    # Process day mapping and coordinates
    df['day'] = df['day'].map({
        0:'Monday', 1:'Tuesday', 2:'Wednesday',
        3:'Thursday', 4:'Friday', 5:'Saturday', 6:'Sunday'
    })
    schedule_df['coordinates'] = schedule_df.apply(
        lambda x: [x['longitude'], x['latitude']], axis=1
    )

    # Create trips layer
    trips_layer = pdk.Layer(
        "TripsLayer",
        df,
        get_path="coordinates",
        get_color=trip_color.value,
        opacity=0.8,
        width_min_pixels=4,
        rounded=True,
        trail_length=1000,
        current_time=500,
        pickable=False,
        auto_highlight=True
    )

    # Create points layer
    point_layer = pdk.Layer(
        "ScatterplotLayer",
        schedule_df,
        pickable=True,
        opacity=0.3,
        stroked=True,
        filled=True,
        radius_scale=25,
        radius_min_pixels=5,
        radius_max_pixels=15,
        line_width_min_pixels=2,
        get_position="coordinates",
        get_timestamps="time",
        get_radius=1,
        get_fill_color=[255, 99, 71],
        get_line_color=[255, 255, 255],
        trail_length=600,
        current_time=250,
        width_min_pixels=5
    )

    center_lat = schedule_df['latitude'].mean()
    center_lon = schedule_df['longitude'].mean()
    # Set view state
    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=zoom,
        bearing=0,
        pitch=0,
        height=600
    )

    # Create and return deck
    # ... existing code ...

# Create and return deck
    return pdk.Deck(
        layers=[trips_layer, point_layer],
        initial_view_state=view_state,
        map_style="dark",
        tooltip={
            "html": """
                <b>Location:</b> {poi_name}<br/>
                <b>Action:</b> {action}<br/>
                <b>Day:</b> {day}<br/>
                <b>Travel Mode:</b> {travel_mode}
            """,
            "style": {
                "backgroundColor": "steelblue",
                "color": "white"
            }
        }
    )

class App:
    def __init__(self, llm):
        self.nodes = Nodes(llm)
        self.edges = Edges()
    def setup(self):
        workflow = StateGraph(WeeklyPlannerState)
        #Nodes 
        workflow.add_node('CreateWeeklySummary', self.nodes.create_weekly_summary)
        workflow.add_node('CreateDailyPlan', self.nodes.create_daily_plan)
        workflow.add_node('POIFinder', self.nodes.find_relevant_pois) 

        # Edges
        workflow.add_edge(START, 'CreateWeeklySummary')
        workflow.add_edge('CreateWeeklySummary', 'CreateDailyPlan')
        workflow.add_edge('CreateDailyPlan', 'POIFinder')
        workflow.add_conditional_edges('POIFinder', self.edges.routing_edge)
        app = workflow.compile()
        return app 

    @staticmethod
    def save_plans_to_pandas(traces):
        # Import pandas
        import pandas as pd
        
        # Create empty list to store plan entries
        all_entries = []
        
        # Get the plans from the last trace
        if traces and isinstance(traces[-1], dict) and 'plans' in traces[-1]:
            all_plans = traces[-1]['plans']
            
            # Map plans to days of week 
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            # Extract entries from each daily plan
            for plan, day in zip(all_plans, days):
                for entry in plan.entries:
                    entry_dict = {
                        'day': day,
                        'time': entry.time,
                        'action': entry.action,
                        'poi_category': entry.poi_category,
                        'location': entry.location,
                        'travel_mode': entry.travel_mode.value if hasattr(entry.travel_mode, 'value') else entry.travel_mode,
                        'poi_name': entry.poi_output.name if entry.poi_output else None,
                        'latitude': entry.poi_output.latitude if entry.poi_output else None,
                        'longitude': entry.poi_output.longitude if entry.poi_output else None,
                        'address': entry.poi_output.address if entry.poi_output else None
                    }
                    all_entries.append(entry_dict)
        
        # Convert to pandas DataFrame
        df = pd.DataFrame(all_entries)
        return df


    @staticmethod
    def post_process_traces(traces):   
        traces = [trace for trace in traces if 'current_day_index' in trace]
        traces = [trace for trace in traces if 'plans' in trace]
        schedule_df = save_plans_to_pandas(traces)
        routes, time, day, travel_mode = client.compute_routes(traces)

        return schedule_df, routes, time, day, travel_mode