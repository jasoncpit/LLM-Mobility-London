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
  const [selectedTraces, setSelectedTraces] = useState({0: true, 1: true, 2: true});

  useEffect(() => {
    const loadTraces = async () => {
      try {
        const traces = await Promise.all([
          fetch('./first_trace.json').then(resp => resp.json()),
          fetch('./second_trace.json').then(resp => resp.json()),
          fetch('./third_trace.json').then(resp => resp.json())
        ]);
        
        console.log('Loaded traces:', traces); // Debug log

        // Define trace colors with 0.8 opacity (multiply RGB values by 0.8)
        const traceColors = {
          0: [65, 182, 196],    // Turquoise blue
          1: [255, 127, 14],    // Orange
          2: [44, 160, 44]      // Green
        };
        
        // Combine all traces with trace-specific colors
        const allTrips = traces.flatMap((trace, traceIndex) => {
          const routes = trace.trip_layer.routes;
          return routes.map(route => ({
            path: route,
            color: [...traceColors[traceIndex], 204],
            traceIndex
          }));
        });
        
        const allPoints = traces.flatMap((trace, traceIndex) => {
          return trace.point_layer.coordinates.map((coord, idx) => ({
            position: coord,
            poi_name: trace.point_layer.poi_name[idx],
            action: trace.point_layer.action[idx],
            time: trace.point_layer.time[idx],
            day: trace.point_layer.day[idx],
            travel_mode: trace.point_layer.travel_mode[idx],
            traceIndex
          }));
        });

        console.log('Processed trips:', allTrips); // Debug log
        console.log('Processed points:', allPoints); // Debug log

        setTripData(allTrips);
        setPointData(allPoints);
      } catch (error) {
        console.error('Error loading traces:', error);
      }
    };

    loadTraces();
  }, []);

  const layers = [
    new TripsLayer({
      id: 'trips',
      data: tripData.filter(d => selectedTraces[d.traceIndex]),
      getPath: d => d.path,
      getColor: d => d.color,
      opacity: 0.8,
      widthMinPixels: 2,
      trailLength: 180,
      fadeTrail: true
    }),
    new ScatterplotLayer({
      id: 'points',
      data: pointData.filter(d => selectedTraces[d.traceIndex]),
      getPosition: d => d.position,
      getColor: d => getColorForMode(d.travel_mode),
      getRadius: 100,
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

  const renderSidePanel = () => {
    return (
      <div style={{
        position: 'absolute',
        top: 20,
        left: 20,
        background: 'white',
        padding: '12px',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
        zIndex: 1
      }}>
        <h3 style={{ margin: '0 0 10px 0' }}>Trace Selection</h3>
        {Object.keys(selectedTraces).map(traceIndex => (
          <div key={traceIndex} style={{ marginBottom: '8px' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <input
                type="checkbox"
                checked={selectedTraces[traceIndex]}
                onChange={() => setSelectedTraces(prev => ({
                  ...prev,
                  [traceIndex]: !prev[traceIndex]
                }))}
              />
              Trace {parseInt(traceIndex) + 1}
            </label>
          </div>
        ))}
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
      {renderSidePanel()}
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
