'use client';

import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import GlobeLanding from '@/components/GlobeLanding';
import ChatInterface from '@/components/ChatInterface';

type AppState = 'globe' | 'chat';

export default function Home() {
  const [state, setState] = useState<AppState>('globe');
  const [selectedLocation, setSelectedLocation] = useState<string | null>(null);

  const handleLocationSelect = (location: string) => {
    setSelectedLocation(location);
    setState('chat');
  };

  return (
    <div className="min-h-screen w-full relative overflow-hidden">
      <AnimatePresence mode="wait">
        {state === 'globe' && (
          <motion.div
            key="globe"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            <GlobeLanding onLocationSelect={handleLocationSelect} />
          </motion.div>
        )}

        {state === 'chat' && selectedLocation && (
          <motion.div
            key="chat"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            <ChatInterface location={selectedLocation} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
