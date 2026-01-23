'use client';

import { useState } from 'react';
import LocationSelector from '@/components/LocationSelector';
import WorldMap from '@/components/WorldMap';
import ChatInterface from '@/components/ChatInterface';
import AnimatedGradientBlobs from '@/components/AnimatedGradientBlobs';

type AppState = 'onboarding' | 'map-zoom' | 'chat';

export default function Home() {
  const [state, setState] = useState<AppState>('onboarding');
  const [selectedLocation, setSelectedLocation] = useState<string | null>(null);

  const handleLocationSelect = (location: string) => {
    setSelectedLocation(location);
    setState('map-zoom');
    
    // After map zoom animation completes, show chat
    setTimeout(() => {
      setState('chat');
    }, 2500);
  };

  return (
    <div className="min-h-screen w-full relative overflow-hidden">
      {/* Background with animated blobs only */}
      <div className="fixed inset-0 bg-white -z-20" />
      <AnimatedGradientBlobs />
      
      {state === 'onboarding' && (
        <div className="min-h-screen flex items-center justify-center p-4 relative z-10">
          <div className="max-w-2xl w-full space-y-8">
            <div className="text-center space-y-4">
              <h1 className="text-5xl font-light text-gray-900 tracking-tight">
                Comask
              </h1>
              <p className="text-xl text-gray-600 font-light">
                Ask away about energy regulations
              </p>
            </div>
            
            <LocationSelector onSelect={handleLocationSelect} />
          </div>
        </div>
      )}

      {state === 'map-zoom' && selectedLocation && (
        <WorldMap 
          targetLocation={selectedLocation}
          onZoomComplete={() => setState('chat')}
        />
      )}

      {state === 'chat' && selectedLocation && (
        <ChatInterface location={selectedLocation} />
      )}
    </div>
  );
}
