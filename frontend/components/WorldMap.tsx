'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import AnimatedGradientBlobs from './AnimatedGradientBlobs';
import WorldMapBackground from './WorldMapBackground';

interface WorldMapProps {
  targetLocation: string;
  onZoomComplete: () => void;
}

// USA/Colorado coordinates on world map (approximate)
// USA is roughly at x: 25-35%, y: 30-50% of world map
// Colorado is roughly at x: 28%, y: 40% of world map
const usaBounds = {
  centerX: 30, // % from left
  centerY: 40, // % from top
};

export default function WorldMap({ targetLocation, onZoomComplete }: WorldMapProps) {
  const [zoomLevel, setZoomLevel] = useState(1);
  const [position, setPosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    // Animate zoom to USA/Colorado region
    const zoomInterval = setInterval(() => {
      setZoomLevel((prev) => {
        if (prev >= 6) {
          clearInterval(zoomInterval);
          setTimeout(() => {
            onZoomComplete();
          }, 500);
          return 6;
        }
        return prev + 0.15;
      });
    }, 50);

    // Animate position to center USA/Colorado
    const positionInterval = setInterval(() => {
      setPosition((prev) => {
        // Calculate target position to center USA/Colorado
        // When zoomed 6x, we need to shift to center the USA region
        const targetX = -usaBounds.centerX * 6 + 50;
        const targetY = -usaBounds.centerY * 6 + 50;
        
        if (Math.abs(prev.x - targetX) < 1 && Math.abs(prev.y - targetY) < 1) {
          clearInterval(positionInterval);
          return { x: targetX, y: targetY };
        }
        
        return {
          x: prev.x + (targetX - prev.x) * 0.1,
          y: prev.y + (targetY - prev.y) * 0.1,
        };
      });
    }, 50);

    return () => {
      clearInterval(zoomInterval);
      clearInterval(positionInterval);
    };
  }, [onZoomComplete]);

  return (
    <div className="fixed inset-0 bg-white flex items-center justify-center overflow-hidden">
      {/* Keep animated blobs in background */}
      <AnimatedGradientBlobs />
      
      {/* World Map with zoom animation */}
      <motion.div
        className="relative w-full h-full"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <div 
          className="absolute inset-0"
          style={{
            transform: `scale(${zoomLevel}) translate(${position.x}%, ${position.y}%)`,
            transformOrigin: 'center center',
            transition: 'transform 0.1s ease-out',
          }}
        >
          {/* World Map SVG */}
          <WorldMapBackground />
        </div>

        {/* Colorado/USA Highlight */}
        <motion.div
          className="absolute"
          style={{
            left: `${usaBounds.centerX}%`,
            top: `${usaBounds.centerY}%`,
            transform: 'translate(-50%, -50%)',
          }}
          initial={{ scale: 0, opacity: 0 }}
          animate={{ 
            scale: zoomLevel > 3 ? 1 : 0, 
            opacity: zoomLevel > 3 ? 1 : 0 
          }}
          transition={{ duration: 0.3 }}
        >
          <div className="relative">
            {/* Pulse ring */}
            <motion.div
              className="absolute inset-0 border-4 border-blue-500 rounded-lg"
              animate={{
                scale: [1, 1.3, 1],
                opacity: [0.6, 0, 0.6],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
              }}
            />
            {/* Colorado marker */}
            <div className="w-20 h-20 border-4 border-white rounded-lg shadow-2xl bg-blue-500/90 backdrop-blur-sm relative z-10">
              <div className="absolute inset-0 flex items-center justify-center text-white font-semibold">
                CO
              </div>
            </div>
          </div>
        </motion.div>

        {/* Loading text */}
        <motion.div
          className="absolute bottom-20 left-1/2 transform -translate-x-1/2 text-center z-20"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <p className="text-gray-700 text-lg font-light bg-white/80 backdrop-blur-sm px-4 py-2 rounded-lg">
            Loading Colorado regulations...
          </p>
        </motion.div>
      </motion.div>
    </div>
  );
}

