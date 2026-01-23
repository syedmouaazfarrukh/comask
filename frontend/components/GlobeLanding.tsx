'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import dynamic from 'next/dynamic';
import { Zap, Database, ChevronRight, Loader2 } from 'lucide-react';

// Dynamically import Globe to avoid SSR issues
const Globe = dynamic(() => import('react-globe.gl'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center">
      <Loader2 className="w-12 h-12 text-cyan-400 animate-spin" />
    </div>
  ),
});

interface GlobeLandingProps {
  onLocationSelect: (location: string) => void;
}

// Colorado coordinates
const COLORADO = {
  lat: 39.5501,
  lng: -105.7821,
  name: 'Colorado',
  code: 'CO',
};

// Energy data center locations for arcs
const energyNodes = [
  { lat: 39.5501, lng: -105.7821, name: 'Colorado', type: 'primary' }, // Colorado (main)
  { lat: 38.9072, lng: -77.0369, name: 'Washington DC', type: 'federal' }, // Federal regulations
  { lat: 40.7128, lng: -74.006, name: 'New York', type: 'exchange' }, // Energy exchange
  { lat: 37.7749, lng: -122.4194, name: 'California', type: 'renewable' }, // Renewable energy hub
  { lat: 29.7604, lng: -95.3698, name: 'Texas', type: 'energy' }, // Energy capital
  { lat: 41.8781, lng: -87.6298, name: 'Chicago', type: 'grid' }, // Grid management
  { lat: 47.6062, lng: -122.3321, name: 'Seattle', type: 'tech' }, // Tech/hydro
  { lat: 33.749, lng: -84.388, name: 'Atlanta', type: 'southeast' }, // Southeast hub
  { lat: 51.5074, lng: -0.1278, name: 'London', type: 'international' }, // International
  { lat: 35.6762, lng: 139.6503, name: 'Tokyo', type: 'international' }, // International
  { lat: 52.52, lng: 13.405, name: 'Berlin', type: 'international' }, // International (renewable leader)
];

// Generate arcs connecting to Colorado
const generateArcs = () => {
  const arcs: any[] = [];
  const coloradoNode = energyNodes[0];

  // Create arcs from Colorado to other US nodes
  energyNodes.slice(1).forEach((node, index) => {
    arcs.push({
      startLat: coloradoNode.lat,
      startLng: coloradoNode.lng,
      endLat: node.lat,
      endLng: node.lng,
      color: node.type === 'federal'
        ? ['rgba(59, 130, 246, 0.8)', 'rgba(59, 130, 246, 0.2)'] // Blue for federal
        : node.type === 'international'
        ? ['rgba(168, 85, 247, 0.6)', 'rgba(168, 85, 247, 0.1)'] // Purple for international
        : ['rgba(34, 211, 238, 0.8)', 'rgba(34, 211, 238, 0.2)'], // Cyan for energy
      stroke: node.type === 'primary' ? 3 : node.type === 'international' ? 1 : 2,
      dashLength: 0.5,
      dashGap: 0.3,
      dashAnimateTime: 2000 + index * 500,
    });
  });

  return arcs;
};

// Generate point markers
const generatePoints = () => {
  return energyNodes.map((node) => ({
    lat: node.lat,
    lng: node.lng,
    name: node.name,
    type: node.type,
    size: node.type === 'primary' ? 1.5 : node.type === 'federal' ? 0.8 : 0.5,
    color: node.type === 'primary'
      ? '#22d3ee'
      : node.type === 'federal'
      ? '#3b82f6'
      : node.type === 'international'
      ? '#a855f7'
      : '#06b6d4',
  }));
};

export default function GlobeLanding({ onLocationSelect }: GlobeLandingProps) {
  const globeRef = useRef<any>(null);
  const [isGlobeReady, setIsGlobeReady] = useState(false);
  const [isZooming, setIsZooming] = useState(false);
  const [hoveredPoint, setHoveredPoint] = useState<string | null>(null);
  const [arcs] = useState(generateArcs);
  const [points] = useState(generatePoints);

  // Set initial globe position and rotation
  useEffect(() => {
    if (globeRef.current && isGlobeReady) {
      // Start with view of Americas
      globeRef.current.pointOfView({ lat: 30, lng: -95, altitude: 2.5 }, 0);

      // Enable auto-rotation
      globeRef.current.controls().autoRotate = true;
      globeRef.current.controls().autoRotateSpeed = 0.3;
      globeRef.current.controls().enableZoom = false;
    }
  }, [isGlobeReady]);

  // Handle Colorado click - zoom in and transition
  const handleColoradoClick = useCallback(() => {
    if (globeRef.current && !isZooming) {
      setIsZooming(true);

      // Stop auto-rotation
      globeRef.current.controls().autoRotate = false;

      // Zoom to Colorado
      globeRef.current.pointOfView(
        { lat: COLORADO.lat, lng: COLORADO.lng, altitude: 0.5 },
        2000
      );

      // Transition to chat after zoom completes
      setTimeout(() => {
        onLocationSelect('colorado');
      }, 2500);
    }
  }, [isZooming, onLocationSelect]);

  // Custom point click handler
  const handlePointClick = useCallback(
    (point: any) => {
      if (point.type === 'primary') {
        handleColoradoClick();
      }
    },
    [handleColoradoClick]
  );

  return (
    <div className="fixed inset-0 bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 overflow-hidden">
      {/* Starfield background */}
      <div className="absolute inset-0 overflow-hidden">
        {[...Array(100)].map((_, i) => (
          <div
            key={i}
            className="absolute w-0.5 h-0.5 bg-white rounded-full animate-pulse"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
              opacity: Math.random() * 0.7 + 0.3,
            }}
          />
        ))}
      </div>

      {/* Globe container */}
      <div className="absolute inset-0">
        <Globe
          ref={globeRef}
          onGlobeReady={() => setIsGlobeReady(true)}
          globeImageUrl="//unpkg.com/three-globe/example/img/earth-blue-marble.jpg"
          bumpImageUrl="//unpkg.com/three-globe/example/img/earth-topology.png"
          backgroundImageUrl=""
          backgroundColor="rgba(0,0,0,0)"
          // Arcs (energy flow lines)
          arcsData={arcs}
          arcColor="color"
          arcStroke="stroke"
          arcDashLength="dashLength"
          arcDashGap="dashGap"
          arcDashAnimateTime="dashAnimateTime"
          arcAltitudeAutoScale={0.3}
          // Points (markers)
          pointsData={points}
          pointLat="lat"
          pointLng="lng"
          pointColor="color"
          pointAltitude={0.01}
          pointRadius="size"
          pointLabel={(d: any) => `<div class="text-white text-sm bg-slate-800/90 px-3 py-2 rounded-lg shadow-xl border border-cyan-500/30">${d.name}</div>`}
          onPointClick={handlePointClick}
          onPointHover={(point: any) => setHoveredPoint(point?.name || null)}
          // Atmosphere
          atmosphereColor="#22d3ee"
          atmosphereAltitude={0.15}
          // Rendering
          animateIn={true}
        />
      </div>

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5, duration: 0.8 }}
        className="absolute top-0 left-0 right-0 z-20 p-8"
      >
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-400 to-blue-500 flex items-center justify-center">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-light text-white tracking-wide">Comask</span>
          </div>
          <div className="flex items-center gap-2 text-cyan-400/70 text-sm">
            <Database className="w-4 h-4" />
            <span>Energy Compliance Intelligence</span>
          </div>
        </div>
      </motion.div>

      {/* Main content overlay */}
      <AnimatePresence>
        {!isZooming && (
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            transition={{ delay: 1, duration: 0.8 }}
            className="absolute bottom-0 left-0 right-0 z-20 p-8 pb-16"
          >
            <div className="max-w-4xl mx-auto text-center space-y-8">
              {/* Title */}
              <div className="space-y-4">
                <h1 className="text-5xl md:text-6xl font-light text-white tracking-tight">
                  Energy Regulation
                  <span className="block text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400">
                    Made Simple
                  </span>
                </h1>
                <p className="text-xl text-slate-400 font-light max-w-2xl mx-auto">
                  Navigate complex energy compliance with AI-powered insights.
                  Ask questions, get cited answers from official sources.
                </p>
              </div>

              {/* Colorado CTA button */}
              <motion.button
                onClick={handleColoradoClick}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="group relative inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-2xl text-white font-medium text-lg shadow-2xl shadow-cyan-500/25 hover:shadow-cyan-500/40 transition-all duration-300"
              >
                <span className="relative z-10">Explore Colorado Regulations</span>
                <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                {/* Glow effect */}
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-cyan-400 to-blue-400 blur-xl opacity-50 group-hover:opacity-75 transition-opacity" />
              </motion.button>

              {/* Stats */}
              <div className="flex items-center justify-center gap-8 text-slate-500 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                  <span>59+ Official Sources</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
                  <span>Real-time Updates</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-purple-400 animate-pulse" />
                  <span>AI-Powered Citations</span>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Zooming overlay */}
      <AnimatePresence>
        {isZooming && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 z-30 flex items-center justify-center bg-slate-950/50 backdrop-blur-sm"
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="text-center space-y-4"
            >
              <Loader2 className="w-12 h-12 text-cyan-400 animate-spin mx-auto" />
              <p className="text-xl text-white font-light">
                Loading Colorado Energy Regulations...
              </p>
              <p className="text-slate-400 text-sm">
                Connecting to official sources
              </p>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Hover tooltip for points */}
      <AnimatePresence>
        {hoveredPoint && !isZooming && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-10 pointer-events-none"
          >
            {hoveredPoint === 'Colorado' && (
              <div className="bg-slate-800/90 border border-cyan-500/50 rounded-xl px-4 py-2 text-cyan-400 text-sm shadow-xl">
                Click to explore Colorado regulations
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Energy flow legend */}
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 1.5, duration: 0.5 }}
        className="absolute bottom-8 left-8 z-20 space-y-2 text-xs text-slate-500"
      >
        <div className="flex items-center gap-2">
          <div className="w-6 h-0.5 bg-gradient-to-r from-cyan-400 to-cyan-400/20" />
          <span>Energy Data Flow</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-6 h-0.5 bg-gradient-to-r from-blue-400 to-blue-400/20" />
          <span>Federal Regulations</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-6 h-0.5 bg-gradient-to-r from-purple-400 to-purple-400/20" />
          <span>International Standards</span>
        </div>
      </motion.div>
    </div>
  );
}
