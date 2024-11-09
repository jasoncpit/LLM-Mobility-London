import React, { useState, useEffect } from 'react';
import { TripsLayer } from '@deck.gl/geo-layers';
import {ScatterplotLayer} from '@deck.gl/layers';
import {DeckGL} from '@deck.gl/react';
import {Map} from 'react-map-gl';
import {BASEMAP} from '@deck.gl/carto';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

function App() {
  const [tripData, setTripData] = useState([]);
  const [pointData, setPointData] = useState([]);
  const [hoverInfo, setHoverInfo] = useState(null);
  const [selectedTraces, setSelectedTraces] = useState({0: true, 1: true, 2: true});
  const [selectedDay, setSelectedDay] = useState('Monday');
  const [isPanelVisible, setIsPanelVisible] = useState(true);
  const [expandedTraces, setExpandedTraces] = useState({});
  const [panelPosition, setPanelPosition] = useState({ x: 20, y: 20 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

  // Add trace information
  const traceInfo = {
    0: { age: 23, occupation: "PhD Student", description: "Daily commute to university" },
    1: { age: 25, occupation: "Professional", description: "Business meetings across the city" },
    2: { age: 17, occupation: "University Student", description: "Sightseeing tour" }
  };

  // Update traceColors to be accessible throughout the component
  const traceColors = {
    0: [65, 182, 196],    // Turquoise blue
    1: [255, 127, 14],    // Orange
    2: [44, 160, 44]      // Green
  };

  useEffect(() => {
    const loadTraces = async () => {
      try {
        const traces = await Promise.all([
          fetch('./first_trace.json').then(resp => resp.json()),
          fetch('./second_trace.json').then(resp => resp.json()),
          fetch('./third_trace.json').then(resp => resp.json())
        ]);
        
        console.log('Loaded traces:', traces); // Debug log

        // Combine all traces with trace-specific colors
        const allTrips = traces.flatMap((trace, traceIndex) => {
          const routes = trace.trip_layer.routes;
          return routes.map((route, idx) => ({
            path: route,
            color: [...traceColors[traceIndex], 204],
            traceIndex,
            day: trace.trip_layer.day[idx]
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
            traceIndex,
            // Add trace info to each point
            traceInfo: traceInfo[traceIndex]
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
      data: tripData.filter(d => 
        selectedTraces[d.traceIndex] && 
        d.day === selectedDay
      ),
      getPath: d => d.path,
      getColor: d => d.color,
      opacity: 0.8,
      widthMinPixels: 2,
      trailLength: 180,
      fadeTrail: true
    }),
    new ScatterplotLayer({
      id: 'points',
      data: pointData.filter(d => selectedTraces[d.traceIndex] && d.day === selectedDay),
      getPosition: d => d.position,
      // Use trace colors instead of travel mode colors
      getColor: d => [...traceColors[d.traceIndex], 204],
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
    const {poi_name, action, day, travel_mode, time, traceInfo, traceIndex} = hoverInfo.object;
    
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
        borderRadius: '4px',
        maxWidth: '300px'
      }}>
        <div><b>Trace {traceIndex + 1}</b></div>
        <div><b>Person:</b> {traceInfo.age} years old, {traceInfo.occupation}</div>
        <div><b>Description:</b> {traceInfo.description}</div>
        <hr style={{ margin: '5px 0', borderColor: 'rgba(255,255,255,0.2)' }} />
        <div><b>Location:</b> {poi_name}</div>
        <div><b>Action:</b> {action}</div>
        <div><b>Day:</b> {day}</div>
        <div><b>Travel Mode:</b> {travel_mode}</div>
        <div><b>Time:</b> {time}</div>
      </div>
    );
  };

  const handleMouseDown = (e) => {
    // Only allow dragging from the header area
    if (e.target.closest('.panel-header')) {
      setIsDragging(true);
      const rect = e.currentTarget.getBoundingClientRect();
      setDragOffset({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
      });
    }
  };

  const handleMouseMove = (e) => {
    if (isDragging) {
      setPanelPosition({
        x: e.clientX - dragOffset.x,
        y: e.clientY - dragOffset.y
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging]);

  const renderSidePanel = () => {
    if (!isPanelVisible) {
      return (
        <button
          onClick={() => setIsPanelVisible(true)}
          style={{
            position: 'absolute',
            top: 20,
            right: 20,
            padding: '8px 12px',
            background: 'white',
            border: 'none',
            borderRadius: '4px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
            cursor: 'pointer',
            zIndex: 1
          }}
        >
          Show Timeline
        </button>
      );
    }

    // Get unique days from pointData
    const uniqueDays = [...new Set(pointData.map(point => point.day))].sort();
    
    // Group activities by trace for the selected day
    const timelineData = pointData
      .filter(point => point.day === selectedDay)
      .reduce((acc, point) => {
        if (!acc[point.traceIndex]) {
          acc[point.traceIndex] = [];
        }
        acc[point.traceIndex].push(point);
        return acc;
      }, {});

    return (
      <div 
        style={{
          position: 'absolute',
          top: panelPosition.y,
          left: panelPosition.x,
          background: 'white',
          padding: '20px',
          borderRadius: '12px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
          zIndex: 1,
          maxWidth: '400px',
          maxHeight: '80vh',
          overflowY: 'auto',
          cursor: isDragging ? 'grabbing' : 'auto',
          userSelect: 'none' // Prevent text selection while dragging
        }}
        onMouseDown={handleMouseDown}
      >
        <div 
          className="panel-header"
          style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center', 
            marginBottom: '15px',
            cursor: 'grab',
            padding: '5px'
          }}
        >
          <h3 style={{ margin: 0 }}>Daily Timeline</h3>
          <button
            onClick={() => setIsPanelVisible(false)}
            style={{
              padding: '4px 8px',
              background: 'none',
              border: '1px solid #ccc',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Hide
          </button>
        </div>

        {/* Day selector dropdown */}
        <select 
          value={selectedDay}
          onChange={(e) => setSelectedDay(e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            marginBottom: '15px',
            borderRadius: '4px'
          }}
        >
          {uniqueDays.map(day => (
            <option key={day} value={day}>{day}</option>
          ))}
        </select>

        {/* Updated Timeline for each trace */}
        {Object.entries(timelineData).map(([traceIndex, activities]) => {
          const trace = traceInfo[traceIndex];
          const color = `rgb(${traceColors[traceIndex].join(',')})`;
          const isExpanded = expandedTraces[traceIndex];
          
          return (
            <div 
              key={traceIndex} 
              style={{ 
                marginBottom: '15px',
                background: '#f8f9fa',
                borderRadius: '8px',
                padding: '12px',
                border: '1px solid #eee'
              }}
            >
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '12px', 
                marginBottom: isExpanded ? '15px' : '0'
              }}>
                <input
                  type="checkbox"
                  checked={selectedTraces[traceIndex]}
                  onChange={() => setSelectedTraces(prev => ({
                    ...prev,
                    [traceIndex]: !prev[traceIndex]
                  }))}
                  style={{
                    width: '18px',
                    height: '18px',
                    cursor: 'pointer'
                  }}
                />
                <div style={{ flex: 1 }}>
                  <div style={{ 
                    fontWeight: 'bold', 
                    color,
                    fontSize: '1.1em',
                    marginBottom: '4px'
                  }}>
                    Trace {parseInt(traceIndex) + 1} - {trace.occupation}
                  </div>
                  <div style={{ fontSize: '0.9em', color: '#666' }}>
                    {trace.age} years old - {trace.description}
                  </div>
                </div>
                <button
                  onClick={() => setExpandedTraces(prev => ({
                    ...prev,
                    [traceIndex]: !prev[traceIndex]
                  }))}
                  style={{
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    padding: '4px',
                    color: '#666',
                    fontSize: '1.2em'
                  }}
                >
                  {isExpanded ? '−' : '+'}
                </button>
              </div>

              {/* Timeline items - only show when expanded */}
              {isExpanded && (
                <div style={{ 
                  marginLeft: '25px',
                  marginTop: '15px',
                  paddingTop: '10px',
                  borderTop: '1px solid #eee'
                }}>
                  {activities.sort((a, b) => a.time.localeCompare(b.time)).map((activity, idx) => (
                    <div 
                      key={idx}
                      style={{
                        borderLeft: `2px solid ${color}`,
                        paddingLeft: '15px',
                        marginBottom: '15px',
                        position: 'relative',
                        transition: 'all 0.2s ease'
                      }}
                    >
                      <div style={{ 
                        position: 'absolute',
                        left: '-5px',
                        top: '0',
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        background: color,
                        border: '2px solid white',
                        boxShadow: '0 0 0 1px ' + color
                      }} />
                      <div style={{ 
                        fontSize: '0.9em', 
                        fontWeight: 'bold',
                        color: '#444'
                      }}>{activity.time}</div>
                      <div style={{
                        margin: '4px 0',
                        color: '#333'
                      }}>{activity.action} at {activity.poi_name}</div>
                      <div style={{ 
                        fontSize: '0.8em',
                        color: '#666',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px'
                      }}>
                        <span style={{
                          padding: '2px 6px',
                          background: '#f0f0f0',
                          borderRadius: '4px'
                        }}>{activity.travel_mode}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
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

export default App;
