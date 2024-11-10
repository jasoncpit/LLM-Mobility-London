import React, { useState, useEffect, useRef, useMemo } from 'react';
import { TripsLayer } from '@deck.gl/geo-layers';
import {ScatterplotLayer} from '@deck.gl/layers';
import {DeckGL} from '@deck.gl/react';
import {Map} from 'react-map-gl';
import {BASEMAP} from '@deck.gl/carto';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import * as d3 from 'd3-ease';
import {FlyToInterpolator} from '@deck.gl/core';

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
  const [selectedPoint, setSelectedPoint] = useState(null);
  const [showAllDays, setShowAllDays] = useState(false);

  // Wrap traceInfo in useMemo
  const traceInfo = useMemo(() => ({
    0: { age: 23, occupation: "Postgraduate Student", description: "Daily commute to university" },
    1: { age: 25, occupation: "Professional", description: "Young professional commuting to work 3 days a week" },
    2: { age: 17, occupation: "University Student", description: "Induction week at university" }
  }), []); // Empty dependency array since this data is static

  // Wrap traceColors in useMemo
  const traceColors = useMemo(() => ({
    0: [65, 182, 196],    // Turquoise blue
    1: [255, 127, 14],    // Orange
    2: [44, 160, 44]      // Green
  }), []); // Empty dependency array since this data is static

  useEffect(() => {
    const loadTraces = async () => {
      try {
        // Load each file separately with error handling
        const traces = await Promise.all([
          fetch('./first_trace.json')
            .then(resp => resp.json())
            .catch(err => {
              console.error('Error loading first_trace.json:', err);
              return null;
            }),
          fetch('./second_trace.json')
            .then(resp => resp.json())
            .catch(err => {
              console.error('Error loading second_trace.json:', err);
              return null;
            }),
          fetch('./third_trace.json')
            .then(resp => resp.json())
            .catch(err => {
              console.error('Error loading third_trace.json:', err);
              return null;
            })
        ]);

        // Filter out any null traces from failed loads
        const validTraces = traces.filter(trace => trace !== null);
        
        // Add debug logging
        console.log('Raw traces:', validTraces);
        
        // Debug the raw data structure
        validTraces.forEach((trace, idx) => {
          console.log(`Trace ${idx} days:`, {
            trip_days: trace.trip_layer.day,
            point_days: trace.point_layer.day
          });
        });

        console.log('Raw traces data:', JSON.stringify(validTraces, null, 2));

        // Combine all traces with trace-specific colors
        const allTrips = validTraces.flatMap((trace, traceIndex) => {
          if (!trace.trip_layer?.routes) {
            console.error(`Missing trip_layer or routes for trace ${traceIndex}`);
            return [];
          }
          const routes = trace.trip_layer.routes;
          return routes.map((route, idx) => {
            const day = trace.trip_layer.day?.[idx] || 'Monday';
            console.log(`Trip ${traceIndex}, route ${idx}, day: ${day}`);
            return {
              path: route,
              color: [...traceColors[traceIndex], 204],
              traceIndex,
              day
            };
          });
        });
        
        const allPoints = validTraces.flatMap((trace, traceIndex) => {
          if (!trace.point_layer?.coordinates) {
            console.error(`Missing point_layer or coordinates for trace ${traceIndex}`);
            return [];
          }
          return trace.point_layer.coordinates.map((coord, idx) => {
            const day = trace.point_layer.day?.[idx] || 'Monday';
            console.log(`Point ${traceIndex}, coord ${idx}, day: ${day}`);
            return {
              position: coord,
              poi_name: trace.point_layer.poi_name?.[idx] || 'Unknown Location',
              action: trace.point_layer.action?.[idx] || 'Unknown Action',
              time: trace.point_layer.time?.[idx] || '00:00',
              day,
              travel_mode: trace.point_layer.travel_mode?.[idx] || 'Unknown',
              traceIndex,
              traceInfo: traceInfo[traceIndex]
            };
          });
        });

        console.log('Processed trips:', allTrips.map(t => ({ day: t.day, traceIndex: t.traceIndex })));
        console.log('Processed points:', allPoints.map(p => ({ day: p.day, traceIndex: p.traceIndex })));

        console.log('Final processed data:', {
          tripData: allTrips,
          pointData: allPoints
        });

        setTripData(allTrips);
        setPointData(allPoints);
      } catch (error) {
        console.error('Error loading traces:', error);
      }
    };

    loadTraces();
  }, [traceColors, traceInfo]);

  const layers = [
    new TripsLayer({
      id: 'trips',
      data: tripData.filter(d => {
        const isVisible = selectedTraces[d.traceIndex] && 
                         (showAllDays || String(d.day).trim() === String(selectedDay).trim());
        console.log(`Trip - trace: ${d.traceIndex}, day: ${d.day}, selected: ${selectedDay}, visible: ${isVisible}`);
        return isVisible;
      }),
      getPath: d => d.path,
      getColor: d => d.color,
      opacity: 0.8,
      widthMinPixels: 2,
      fadeTrail: false,
      trailLength: 1000,
      currentTime: 1000
    }),
    new ScatterplotLayer({
      id: 'points',
      data: pointData.filter(d => {
        const isVisible = selectedTraces[d.traceIndex] && 
                         (showAllDays || String(d.day).trim() === String(selectedDay).trim());
        console.log(`Point - trace: ${d.traceIndex}, day: ${d.day}, selected: ${selectedDay}, visible: ${isVisible}`);
        return isVisible;
      }),
      getPosition: d => d.position,
      getColor: d => {
        const isSelected = selectedPoint && 
          selectedPoint.some(p => 
            p.position[0] === d.position[0] && 
            p.position[1] === d.position[1] &&
            p.day === d.day &&
            p.action === d.action
          );
        return isSelected ? [0, 153, 255, 255] : [...traceColors[d.traceIndex], 204];
      },
      getRadius: d => {
        const isSelected = selectedPoint && 
          selectedPoint.some(p => 
            p.position[0] === d.position[0] && 
            p.position[1] === d.position[1] &&
            p.day === d.day &&
            p.action === d.action
          );
        return isSelected ? 200 : 100;
      },
      opacity: 0.8,
      pickable: true,
      onHover: info => setHoverInfo(info),
      transitions: {
        getRadius: {
          duration: 500,
          easing: d3.easeCubicInOut
        },
        getColor: {
          duration: 500,
          easing: d3.easeCubicInOut
        }
      },
      onClick: (info) => {
        if (info.object) {
          const {position, traceIndex, day, action} = info.object;
          
          // Find all points at this location
          const pointsAtLocation = pointData.filter(p => 
            p.position[0] === position[0] && 
            p.position[1] === position[1] &&
            p.day === day &&
            p.action === action &&
            selectedTraces[p.traceIndex]
          );

          // Update selected point
          setSelectedPoint(
            selectedPoint && 
            selectedPoint.some(p => 
              p.position[0] === position[0] && 
              p.position[1] === position[1] &&
              p.day === day &&
              p.action === action
            ) 
              ? null 
              : pointsAtLocation
          );

          // Expand the trace containing this point
          setExpandedTraces(prev => ({
            ...prev,
            [traceIndex]: true
          }));

          // Zoom to the point
          zoomToPoint(position[0], position[1]);
        }
      },
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
    if (e.target.closest('.panel-header')) {
      setIsDragging(true);
      const rect = e.currentTarget.getBoundingClientRect();
      setDragOffset({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
      });
    }
  };

  useEffect(() => {
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

    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, dragOffset]);

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

    // Get unique days from pointData, including days from all traces regardless of selection
    const uniqueDays = pointData.length > 0 
      ? [...new Set(pointData.map(point => point.day))].sort()
      : [];
    
    // Group activities by trace for all traces, not just selected ones
    const timelineData = pointData
      .reduce((acc, point) => {
        if (!acc[point.traceIndex]) {
          acc[point.traceIndex] = [];
        }
        // Only add unique points
        const isDuplicate = acc[point.traceIndex].some(existing => 
          existing.time === point.time && 
          existing.position[0] === point.position[0] && 
          existing.position[1] === point.position[1] &&
          existing.day === point.day
        );
        if (!isDuplicate) {
          acc[point.traceIndex].push(point);
        }
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
          userSelect: 'none',
        }}
        onMouseDown={(e) => {
          if (e.target.closest('.panel-header')) {
            handleMouseDown(e);
            e.stopPropagation();
          }
        }}
      >
        <div 
          className="panel-header"
          style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center', 
            marginBottom: '15px',
            cursor: isDragging ? 'grabbing' : 'grab',
            padding: '5px',
            pointerEvents: 'auto',
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

        {/* Updated display mode toggle */}
        <div style={{
          display: 'flex',
          gap: '10px',
          marginBottom: '15px',
          alignItems: 'center'
        }}>
          <select 
            value={selectedDay}
            onChange={(e) => setSelectedDay(e.target.value)}
            disabled={showAllDays}
            style={{
              flex: 1,
              padding: '8px',
              borderRadius: '4px',
              opacity: showAllDays ? 0.5 : 1
            }}
          >
            {uniqueDays.map(day => (
              <option key={day} value={day}>{day}</option>
            ))}
          </select>
          <button
            onClick={() => setShowAllDays(prev => !prev)}
            style={{
              padding: '8px 12px',
              background: showAllDays ? '#007bff' : '#f8f9fa',
              color: showAllDays ? 'white' : '#333',
              border: '1px solid #dee2e6',
              borderRadius: '4px',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              whiteSpace: 'nowrap'
            }}
          >
            {showAllDays ? 'Show Single Day' : 'Show All Days'}
          </button>
        </div>

        {/* Updated Timeline for each trace - always show all traces */}
        {Object.entries(timelineData).map(([traceIndex, activities]) => {
          const trace = traceInfo[traceIndex];
          const color = `rgb(${traceColors[traceIndex].join(',')})`;
          const isExpanded = expandedTraces[traceIndex];
          const isSelected = selectedTraces[traceIndex];
          
          return (
            <div key={traceIndex} 
              style={{ 
                marginBottom: '15px',
                background: '#f8f9fa',
                borderRadius: '8px',
                padding: '12px',
                border: '1px solid #eee',
                opacity: isSelected ? 1 : 0.7,
                transition: 'opacity 0.3s ease'
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
                  {isExpanded ? '-': '+'}
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
                  {activities
                    .filter(activity => showAllDays || String(activity.day).trim() === String(selectedDay).trim())
                    .sort((a, b) => a.time.localeCompare(b.time))
                    .map((activity, idx) => {
                      const pointsAtLocation = pointData.filter(p => 
                        p.position[0] === activity.position[0] && 
                        p.position[1] === activity.position[1] &&
                        p.day === activity.day &&
                        p.action === activity.action &&
                        selectedTraces[p.traceIndex]
                      );

                      return (
                        <div 
                          key={idx}
                          style={{
                            borderLeft: `2px solid ${color}`,
                            paddingLeft: '15px',
                            marginBottom: '15px',
                            position: 'relative',
                            cursor: 'pointer',
                            background: selectedPoint && 
                              selectedPoint.some(p => 
                                p.position[0] === activity.position[0] && 
                                p.position[1] === activity.position[1] &&
                                p.day === activity.day &&
                                p.action === activity.action
                              ) ? 'rgba(0, 153, 255, 0.1)' : 'transparent',
                            transition: 'all 0.3s ease-in-out',
                            transform: selectedPoint && 
                              selectedPoint.some(p => 
                                p.position[0] === activity.position[0] && 
                                p.position[1] === activity.position[1] &&
                                p.day === activity.day &&
                                p.action === activity.action
                              ) ? 'scale(1.02)' : 'scale(1)',
                            boxShadow: selectedPoint && 
                              selectedPoint.some(p => 
                                p.position[0] === activity.position[0] && 
                                p.position[1] === activity.position[1] &&
                                p.day === activity.day &&
                                p.action === activity.action
                              ) ? '0 2px 8px rgba(0, 153, 255, 0.2)' : 'none',
                            borderRadius: '4px',
                            padding: '8px'
                          }}
                          onClick={(e) => {
                            // Prevent event from bubbling up
                            e.stopPropagation();
                            
                            setSelectedPoint(
                              selectedPoint && 
                              selectedPoint.some(p => 
                                p.position[0] === activity.position[0] && 
                                p.position[1] === activity.position[1] &&
                                p.day === activity.day &&
                                p.action === activity.action
                              ) 
                                ? null 
                                : pointsAtLocation
                            );
                            
                            setExpandedTraces(prev => ({
                              ...prev,
                              [activity.traceIndex]: true
                            }));

                            zoomToPoint(activity.position[0], activity.position[1]);
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
                      );
                    })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    );
  };

  const deckRef = useRef(null);

  const zoomToPoint = (longitude, latitude) => {
    if (deckRef.current) {
      const currentViewState = deckRef.current.viewState || {
        longitude: -0.1278,
        latitude: 51.5574,
        zoom: 11,
        pitch: 0,
        bearing: 0
      };

      // Create a new viewState object instead of directly modifying deck props
      const newViewState = {
        ...currentViewState,
        longitude: longitude + (currentViewState.longitude - longitude) * 0.3,
        latitude: latitude + (currentViewState.latitude - latitude) * 0.3,
        zoom: Math.min(currentViewState.zoom + 0.3, 13),
        transitionDuration: 1000,
        transitionInterpolator: new FlyToInterpolator(),
      };

      // Use onViewStateChange callback to update the view
      deckRef.current.deck.setProps({
        initialViewState: newViewState,
        onViewStateChange: ({viewState}) => {
          // This ensures the controller remains interactive after transition
          deckRef.current.deck.setProps({
            initialViewState: viewState
          });
        }
      });
    }
  };

  return (
    <>
      <DeckGL
        ref={deckRef}
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
          mapStyle={BASEMAP.DARK_MATTER}
          mapLib={maplibregl}
        />
      </DeckGL>
      {renderTooltip()}
      {renderSidePanel()}
    </>
  );
}

export default App;
