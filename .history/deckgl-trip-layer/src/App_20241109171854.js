import React, { useState, useEffect } from 'react';
import { TripsLayer } from '@deck.gl/geo-layers';
import {ScatterplotLayer} from '@deck.gl/layers';
import {DeckGL} from '@deck.gl/react';
import {Map} from 'react-map-gl';
import {BASEMAP} from '@deck.gl/carto';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

function App() {
  const [time, setTime] = useState(0);
  const [currentDay, setCurrentDay] = useState(0);
  const [tripData, setTripData] = useState([]);
  const [pointData, setPointData] = useState([]);

  useEffect(() => {
    // Fetch and load the trace data
    const loadTraces = async () => {
      const traces = await Promise.all([
        fetch('data/first_trace.json').then(resp => resp.json()),
        fetch('data/second_trace.json').then(resp => resp.json()),
        fetch('data/third_trace.json').then(resp => resp.json())
      ]);
      
      // Combine all traces
      const allTrips = traces.flatMap(trace => {
        const routes = trace.trip_layer.routes;
        return routes.map(route => ({
          path: route,
          timestamps: trace.trip_layer.time,
          day: trace.trip_layer.day,
          color: getColorForMode(trace.trip_layer.travel_mode)
        }));
      });

      const allPoints = traces.flatMap(trace => {
        return trace.point_layer.coordinates.map((coord, idx) => ({
          position: coord,
          timestamp: trace.point_layer.time[idx],
          day: trace.point_layer.day[idx],
          name: trace.point_layer.poi_name[idx],
          action: trace.point_layer.action[idx]
        }));
      });

      setTripData(allTrips);
      setPointData(allPoints);
    };

    loadTraces();

    // Animate through time and days
    const interval = setInterval(() => {
      setTime(t => {
        const newTime = (t + 0.1) % 24; // 24 hour cycle
        if (newTime < t) {
          setCurrentDay(d => (d + 1) % 7); // Advance to next day when time resets
        }
        return newTime;
      });
    }, 100);

    return () => clearInterval(interval);
  }, []);

  const layers = [
    new TripsLayer({
      id: 'trips',
      data: tripData,
      getPath: d => d.path,
      getTimestamps: d => d.timestamps,
      getColor: d => d.color,
      opacity: 0.8,
      widthMinPixels: 2,
      trailLength: 1,
      currentTime: time,
      fadeTrail: true,
      // Filter for current day
      getFilterValue: d => d.day === currentDay,
      filterRange: [0, 1]
    }),
    new ScatterplotLayer({
      id: 'points',
      data: pointData,
      getPosition: d => d.position,
      getColor: d => d.action === 'arrival' ? [0, 255, 0] : [255, 0, 0],
      getRadius: 50,
      opacity: 0.8,
      pickable: true,
      // Filter points for current day and approximate current time
      visible: d => d.day === currentDay && Math.abs(d.timestamp - time) < 0.5
    })
  ];

  return (
    <DeckGL
      initialViewState={{
        longitude: -122.45,
        latitude: 37.76,
        zoom: 12,
        pitch: 45
      }}
      controller={true}
      layers={layers}
    >
      <Map
        mapStyle={BASEMAP.POSITRON}
        mapLib={maplibregl}
      />
    </DeckGL>
  );
}

// Helper function to get colors for different travel modes
function getColorForMode(mode) {
  const colors = {
    'walking': [0, 255, 0],
    'driving': [255, 0, 0],
    'transit': [0, 0, 255],
    // Add more modes as needed
    'default': [128, 128, 128]
  };
  return colors[mode] || colors.default;
}

export default App;
