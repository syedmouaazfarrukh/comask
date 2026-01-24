'use client';

import { useState, useEffect, memo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Zap, Database, ChevronRight, Loader2, MapPin } from 'lucide-react';
import {
  ComposableMap,
  Geographies,
  Geography,
  Line,
  Marker,
} from 'react-simple-maps';

interface GlobeLandingProps {
  onLocationSelect: (location: string) => void;
}

// World map TopoJSON URL
const geoUrl = 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json';

// Energy connection points with actual coordinates [longitude, latitude]
const energyNodes = [
  { id: 'colorado', name: 'Colorado', coordinates: [-105.5, 39.0] as [number, number], primary: true },
  { id: 'dc', name: 'Washington DC', coordinates: [-77.0, 38.9] as [number, number], type: 'federal' },
  { id: 'california', name: 'California', coordinates: [-119.4, 36.8] as [number, number], type: 'renewable' },
  { id: 'texas', name: 'Texas', coordinates: [-99.9, 31.5] as [number, number], type: 'energy' },
  { id: 'chicago', name: 'Chicago', coordinates: [-87.6, 41.9] as [number, number], type: 'grid' },
  { id: 'newyork', name: 'New York', coordinates: [-74.0, 40.7] as [number, number], type: 'exchange' },
  { id: 'seattle', name: 'Seattle', coordinates: [-122.3, 47.6] as [number, number], type: 'hydro' },
  { id: 'london', name: 'London', coordinates: [-0.1, 51.5] as [number, number], type: 'international' },
  { id: 'brussels', name: 'Brussels', coordinates: [4.4, 50.8] as [number, number], type: 'international' },
  { id: 'tokyo', name: 'Tokyo', coordinates: [139.7, 35.7] as [number, number], type: 'international' },
  { id: 'sydney', name: 'Sydney', coordinates: [151.2, -33.9] as [number, number], type: 'international' },
  { id: 'dubai', name: 'Dubai', coordinates: [55.3, 25.3] as [number, number], type: 'international' },
];

// Generate connection lines from Colorado
const connections = energyNodes
  .filter(n => !n.primary)
  .map(node => ({
    from: energyNodes[0].coordinates,
    to: node.coordinates,
    type: node.type,
    name: node.name,
  }));

const getLineColor = (type: string) => {
  switch (type) {
    case 'federal': return '#3b82f6';
    case 'international': return '#a855f7';
    default: return '#22d3ee';
  }
};

// Memoized map component for performance
const WorldMap = memo(function WorldMap({
  hoveredNode,
  setHoveredNode,
  onColoradoClick
}: {
  hoveredNode: string | null;
  setHoveredNode: (id: string | null) => void;
  onColoradoClick: () => void;
}) {
  return (
    <ComposableMap
      projection="geoMercator"
      projectionConfig={{
        scale: 150,
        center: [0, 30],
      }}
      style={{ width: '100%', height: '100%' }}
    >
      {/* Countries */}
      <Geographies geography={geoUrl}>
        {({ geographies }) =>
          geographies.map((geo) => (
            <Geography
              key={geo.rsmKey}
              geography={geo}
              fill="#1e293b"
              stroke="#334155"
              strokeWidth={0.5}
              style={{
                default: { outline: 'none' },
                hover: { outline: 'none', fill: '#334155' },
                pressed: { outline: 'none' },
              }}
            />
          ))
        }
      </Geographies>

      {/* Connection lines */}
      {connections.map((conn, i) => (
        <Line
          key={i}
          from={conn.from}
          to={conn.to}
          stroke={getLineColor(conn.type || '')}
          strokeWidth={1.5}
          strokeLinecap="round"
          strokeOpacity={0.6}
          style={{
            filter: 'drop-shadow(0 0 4px ' + getLineColor(conn.type || '') + ')',
          }}
        />
      ))}

      {/* Energy node markers */}
      {energyNodes.map((node) => (
        <Marker
          key={node.id}
          coordinates={node.coordinates}
          onMouseEnter={() => setHoveredNode(node.id)}
          onMouseLeave={() => setHoveredNode(null)}
          onClick={node.primary ? onColoradoClick : undefined}
          style={{ cursor: node.primary ? 'pointer' : 'default' }}
        >
          {node.primary ? (
            // Colorado marker
            <g>
              <circle r={12} fill="#22d3ee" opacity={0.2} />
              <circle r={8} fill="#22d3ee" opacity={0.3} />
              <circle r={5} fill="#22d3ee" />
            </g>
          ) : (
            // Other markers
            <circle
              r={4}
              fill={getLineColor(node.type || '')}
              style={{
                filter: 'drop-shadow(0 0 4px ' + getLineColor(node.type || '') + ')',
              }}
            />
          )}
        </Marker>
      ))}
    </ComposableMap>
  );
});

export default function GlobeLanding({ onLocationSelect }: GlobeLandingProps) {
  const [isZooming, setIsZooming] = useState(false);
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleColoradoClick = () => {
    if (!isZooming) {
      setIsZooming(true);
      setTimeout(() => {
        onLocationSelect('colorado');
      }, 1500);
    }
  };

  if (!mounted) return null;

  return (
    <div className="fixed inset-0 bg-slate-950 overflow-hidden">
      {/* Gradient overlay at top */}
      <div className="absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-slate-950 via-slate-950/80 to-transparent z-10" />

      {/* Gradient overlay at bottom */}
      <div className="absolute inset-x-0 bottom-0 h-64 bg-gradient-to-t from-slate-950 via-slate-950/90 to-transparent z-10" />

      {/* World Map Background - Full screen */}
      <motion.div
        className="absolute inset-0"
        animate={isZooming ? {
          scale: 3,
          x: '50%',
          opacity: 0
        } : {
          scale: 1,
          x: 0,
          opacity: 1
        }}
        transition={{ duration: 1.5, ease: 'easeInOut' }}
      >
        <WorldMap
          hoveredNode={hoveredNode}
          setHoveredNode={setHoveredNode}
          onColoradoClick={handleColoradoClick}
        />
      </motion.div>

      {/* Animated pulse rings for Colorado (overlay) */}
      {!isZooming && (
        <div className="absolute inset-0 pointer-events-none z-5">
          <svg className="w-full h-full" style={{ position: 'absolute' }}>
            <defs>
              <radialGradient id="pulseGrad">
                <stop offset="0%" stopColor="#22d3ee" stopOpacity="0.4" />
                <stop offset="100%" stopColor="#22d3ee" stopOpacity="0" />
              </radialGradient>
            </defs>
            {/* Pulse animation positioned roughly where Colorado is */}
            <motion.circle
              cx="32%"
              cy="42%"
              fill="url(#pulseGrad)"
              initial={{ r: 10 }}
              animate={{ r: 40, opacity: [0.6, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
            <motion.circle
              cx="32%"
              cy="42%"
              fill="url(#pulseGrad)"
              initial={{ r: 10 }}
              animate={{ r: 30, opacity: [0.4, 0] }}
              transition={{ duration: 2, repeat: Infinity, delay: 0.5 }}
            />
          </svg>
        </div>
      )}

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.8 }}
        className="absolute top-0 left-0 right-0 z-20 p-6 md:p-8"
      >
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img
              src="/logow.png"
              alt="Comask"
              className="h-10 w-auto"
            />
          </div>
          <div className="hidden md:flex items-center gap-2 text-cyan-400/70 text-sm">
            <Database className="w-4 h-4" />
            <span>Energy Compliance Intelligence</span>
          </div>
        </div>
      </motion.div>

      {/* Hovered node tooltip */}
      <AnimatePresence>
        {hoveredNode && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="fixed top-1/2 left-1/2 transform -translate-x-1/2 z-30 pointer-events-none"
          >
            <div className="bg-slate-800/90 backdrop-blur-sm px-4 py-2 rounded-lg border border-slate-700">
              <span className="text-white text-sm font-medium">
                {energyNodes.find(n => n.id === hoveredNode)?.name}
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Bottom content - positioned higher */}
      <AnimatePresence>
        {!isZooming && (
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            transition={{ delay: 0.5, duration: 0.8 }}
            className="absolute bottom-0 left-0 right-0 z-20 p-6 md:p-8 pb-20 md:pb-28"
          >
            <div className="max-w-4xl mx-auto text-center space-y-6 md:space-y-8">
              {/* Title */}
              <div className="space-y-3 md:space-y-4">
                <h1 className="text-4xl md:text-5xl lg:text-6xl font-light text-white tracking-tight">
                  Energy Regulation
                  <span className="block text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400">
                    Made Simple
                  </span>
                </h1>
                <p className="text-lg md:text-xl text-slate-400 font-light max-w-2xl mx-auto">
                  Navigate complex energy compliance with AI-powered insights.
                  Ask questions, get cited answers from official sources.
                </p>
              </div>

              {/* CTA Button */}
              <motion.button
                onClick={handleColoradoClick}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="group relative inline-flex items-center gap-3 px-6 md:px-8 py-3 md:py-4 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-2xl text-white font-medium text-base md:text-lg shadow-2xl shadow-cyan-500/25 hover:shadow-cyan-500/40 transition-all duration-300"
              >
                <MapPin className="w-5 h-5" />
                <span className="relative z-10">Explore Colorado Regulations</span>
                <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-cyan-400 to-blue-400 blur-xl opacity-50 group-hover:opacity-75 transition-opacity" />
              </motion.button>

              {/* Stats */}
              <div className="flex flex-wrap items-center justify-center gap-4 md:gap-8 text-slate-500 text-xs md:text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                  <span>59+ Official Sources</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
                  <span>Federal Regulations</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-purple-400 animate-pulse" />
                  <span>International Standards</span>
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
            className="absolute inset-0 z-30 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm"
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

      {/* Legend */}
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 1, duration: 0.5 }}
        className="absolute bottom-8 left-8 z-20 space-y-2 text-xs text-slate-400 hidden md:block"
      >
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-cyan-400" />
          <span>Energy Grid Connections</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-blue-500" />
          <span>Federal Regulatory Bodies</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-purple-500" />
          <span>International Standards</span>
        </div>
      </motion.div>
    </div>
  );
}
