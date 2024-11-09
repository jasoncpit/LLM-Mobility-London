import React, { useState, useEffect } from 'react';
import DeckGL from '@deck.gl/react';
import { TripsLayer } from '@deck.gl/geo-layers';
import { StaticMap } from 'react-map-gl';

const MAPBOX_TOKEN = 'YOUR_MAPBOX_ACCESS_TOKEN'; // Replace with your Mapbox token

function App() {
  const [time, setTime] = useState(0);
  const [tripData, setTripData] = useState([]);

  useEffect(() => {
    // Fetch trip data or set it manually
    setTripData([
      {
        path: [[-122.45, 37.78], [-122.46, 37.76], [-122.48, 37.73]],
        timestamps: [0, 10, 20],
        color: [255, 0, 0]
      }
    ]);

    // Update time for animation
    const interval = setInterval(() => {
      setTime(t => (t + 0.1) % 30); // Adjust time progression as needed
    }, 100);
    return () => clearInterval(interval);
  }, []);

  const layer = new TripsLayer({
    id: 'trips',
    data: tripData,
    getPath: d => d.path,
    getTimestamps: d => d.timestamps,
    getColor: d => d.color,
    opacity: 0.8,
    widthMinPixels: 2,
    trailLength: 5,
    currentTime: time
  });

  return (
    <DeckGL
      initialViewState={{
        longitude: -122.45,
        latitude: 37.76,
        zoom: 12,
        pitch: 45
      }}
      controller={true}
      layers={[layer]}
    >
      <StaticMap mapboxApiAccessToken={MAPBOX_TOKEN} />
    </DeckGL>
  );
}

export default App;
