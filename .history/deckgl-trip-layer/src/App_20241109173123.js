import React, { useState, useEffect } from 'react';
import { TripsLayer } from '@deck.gl/geo-layers';
import {ScatterplotLayer} from '@deck.gl/layers';
import {DeckGL} from '@deck.gl/react';
import {Map} from 'react-map-gl';
import {BASEMAP} from '@deck.gl/carto';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import {Tooltip} from '@deck.gl/core';

function App() {
  const [tripData, setTripData] = useState([]);
  const [pointData, setPointData] = useState([]);
  const [hoverInfo, setHoverInfo] = useState(null);

  useEffect(() => {
    // Fetch and load the trace data
    const loadTraces = async () => {
      const traces = await Promise.all([
        fetch('./first_trace.json').then(resp => resp.json()),
        fetch('./second_trace.json').then(resp => resp.json()),
        fetch('./third_trace.json').then(resp => resp.json())
      ]);
      
      // Combine all traces
      const allTrips = traces.flatMap(trace => {
        const routes = trace.trip_layer.routes;
        return routes.map(route => ({
          path: route,
          color: getColorForMode(trace.trip_layer.travel_mode)
        }));
      });
      
      const allPoints = traces.flatMap(trace => {
        return trace.point_layer.coordinates.map((coord, idx) => ({
          position: coord,
          poi_name: trace.point_layer.poi_name[idx],
          action: trace.point_layer.action[idx],
          time: trace.point_layer.time[idx],
          day: trace.point_layer.day[idx],
          travel_mode: trace.point_layer.travel_mode[idx]
        }));
      });

      setTripData(allTrips);
      setPointData(allPoints);
    };

    loadTraces();
  }, []);

  const layers = [
    new TripsLayer({
      id: 'trips',
      data: tripData,
      getPath: d => d.path,
      getColor: d => d.color,
      opacity: 0.8,
      widthMinPixels: 2,
    }),
    new ScatterplotLayer({
      id: 'points',
      data: pointData,
      getPosition: d => d.position,
      getColor: d => d.action === 'arrival' ? [0, 255, 0] : [255, 0, 0],
      getRadius: 50,
      opacity: 0.8,
      pickable: true,
      onHover: info => setHoverInfo(info)
    })
  ];

  const renderTooltip = () => {
    if (!hoverInfo?.object) {
      return null;
    }
    const {poi_name, action, day, travel_mode, time} = hoverInfo.object;
    
    return (
      <div style={{
        position: 'absolute',
        zIndex: 1,
        pointerEvents: 'none',
        left: hoverInfo.x,
        top: hoverInfo.y,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: '10px',
        color: 'white',
        borderRadius: '4px'
      }}>
        <div><b>Location:</b> {poi_name}</div>
        <div><b>Action:</b> {action}</div>
        <div><b>Day:</b> {day}</div>
        <div><b>Travel Mode:</b> {travel_mode}</div>
        <div><b>Time:</b> {time}</div>
      </div>
    );
  };

  return (
    <>
      <DeckGL
        initialViewState={{
          longitude: -0.1278,
          latitude: 51.5574,
          zoom: 11,
          pitch: 0
        }}
        controller={true}
        layers={layers}
      >
        <Map
          mapStyle={BASEMAP.POSITRON}
          mapLib={maplibregl}
        />
      </DeckGL>
      {renderTooltip()}
    </>
  );
}

// Helper function to get colors for different travel modes
function getColorForMode(mode) {
  const colors = {
    'WALK': [0, 255, 0],
    'DRIVE': [255, 0, 0],
    'TRANSIT': [0, 0, 255],
    // Add more modes as needed
    'default': [128, 128, 128]
  };
  return colors[mode] || colors.default;
}

export default App;
