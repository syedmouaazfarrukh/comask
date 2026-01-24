'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Zap, Database, ChevronRight, Loader2, Globe2 } from 'lucide-react';

interface GlobeLandingProps {
  onLocationSelect: (location: string) => void;
}

// Energy connection points
const energyNodes = [
  { id: 'colorado', name: 'Colorado', x: 25, y: 42, primary: true },
  { id: 'dc', name: 'Washington DC', x: 32, y: 40, type: 'federal' },
  { id: 'california', name: 'California', x: 15, y: 43, type: 'renewable' },
  { id: 'texas', name: 'Texas', x: 23, y: 50, type: 'energy' },
  { id: 'chicago', name: 'Chicago', x: 28, y: 38, type: 'grid' },
  { id: 'newyork', name: 'New York', x: 34, y: 39, type: 'exchange' },
  { id: 'seattle', name: 'Seattle', x: 14, y: 32, type: 'hydro' },
  { id: 'london', name: 'London', x: 48, y: 30, type: 'international' },
  { id: 'berlin', name: 'Berlin', x: 52, y: 28, type: 'international' },
  { id: 'tokyo', name: 'Tokyo', x: 82, y: 38, type: 'international' },
];

// Generate connection lines from Colorado
const connections = energyNodes
  .filter(n => !n.primary)
  .map(node => ({
    from: energyNodes[0],
    to: node,
    type: node.type,
  }));

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
      }, 2000);
    }
  };

  const getLineColor = (type: string) => {
    switch (type) {
      case 'federal': return '#3b82f6';
      case 'international': return '#a855f7';
      default: return '#22d3ee';
    }
  };

  if (!mounted) return null;

  return (
    <div className="fixed inset-0 bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 overflow-hidden">
      {/* Animated starfield */}
      <div className="absolute inset-0 overflow-hidden">
        {[...Array(150)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-0.5 h-0.5 bg-white rounded-full"
            initial={{ opacity: 0 }}
            animate={{
              opacity: [0.2, 0.8, 0.2],
              scale: [1, 1.2, 1],
            }}
            transition={{
              duration: 2 + Math.random() * 3,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
          />
        ))}
      </div>

      {/* Globe visualization */}
      <div className="absolute inset-0 flex items-center justify-center">
        <motion.div
          className="relative"
          animate={isZooming ? { scale: 3, opacity: 0 } : { scale: 1, opacity: 1 }}
          transition={{ duration: 2, ease: 'easeInOut' }}
        >
          {/* Globe container */}
          <div className="relative w-[600px] h-[600px]">
            {/* Rotating globe with world map */}
            <motion.div
              className="absolute inset-0 rounded-full overflow-hidden"
              animate={{ rotateY: isZooming ? 0 : 360 }}
              transition={{ duration: 60, repeat: Infinity, ease: 'linear' }}
              style={{ transformStyle: 'preserve-3d', perspective: 1000 }}
            >
              {/* Globe base */}
              <div
                className="absolute inset-0 rounded-full"
                style={{
                  background: 'radial-gradient(circle at 30% 30%, #1e3a5f 0%, #0f172a 50%, #020617 100%)',
                  boxShadow: 'inset -30px -30px 60px rgba(0,0,0,0.5), inset 20px 20px 40px rgba(34, 211, 238, 0.1)',
                }}
              />

              {/* Continental outlines - simplified SVG */}
              <svg
                className="absolute inset-0 w-full h-full opacity-30"
                viewBox="0 0 100 100"
              >
                {/* North America */}
                <path
                  d="M15,25 Q20,20 30,22 L35,28 Q38,35 35,42 L28,48 Q22,52 18,48 L12,40 Q10,32 15,25"
                  fill="none"
                  stroke="#22d3ee"
                  strokeWidth="0.5"
                />
                {/* South America */}
                <path
                  d="M28,55 Q32,52 34,58 L32,70 Q28,78 25,75 L23,65 Q24,58 28,55"
                  fill="none"
                  stroke="#22d3ee"
                  strokeWidth="0.5"
                />
                {/* Europe */}
                <path
                  d="M45,22 Q52,20 55,25 L58,30 Q55,35 50,33 L45,28 Q43,25 45,22"
                  fill="none"
                  stroke="#22d3ee"
                  strokeWidth="0.5"
                />
                {/* Africa */}
                <path
                  d="M48,38 Q55,35 58,42 L56,55 Q52,62 48,58 L45,48 Q44,42 48,38"
                  fill="none"
                  stroke="#22d3ee"
                  strokeWidth="0.5"
                />
                {/* Asia */}
                <path
                  d="M60,22 Q75,18 85,25 L88,35 Q85,42 78,40 L68,38 Q62,35 60,28 L60,22"
                  fill="none"
                  stroke="#22d3ee"
                  strokeWidth="0.5"
                />
                {/* Australia */}
                <path
                  d="M78,55 Q85,52 88,58 L86,65 Q82,68 78,65 L76,60 Q76,56 78,55"
                  fill="none"
                  stroke="#22d3ee"
                  strokeWidth="0.5"
                />
              </svg>

              {/* Grid lines */}
              <svg className="absolute inset-0 w-full h-full opacity-10" viewBox="0 0 100 100">
                {/* Latitude lines */}
                {[20, 35, 50, 65, 80].map((y) => (
                  <ellipse
                    key={`lat-${y}`}
                    cx="50"
                    cy={y}
                    rx={45 - Math.abs(y - 50) * 0.5}
                    ry="3"
                    fill="none"
                    stroke="#22d3ee"
                    strokeWidth="0.3"
                  />
                ))}
                {/* Longitude lines */}
                {[0, 30, 60, 90, 120, 150].map((angle) => (
                  <ellipse
                    key={`lng-${angle}`}
                    cx="50"
                    cy="50"
                    rx="3"
                    ry="45"
                    fill="none"
                    stroke="#22d3ee"
                    strokeWidth="0.3"
                    transform={`rotate(${angle} 50 50)`}
                  />
                ))}
              </svg>
            </motion.div>

            {/* Atmosphere glow */}
            <div
              className="absolute inset-[-20px] rounded-full pointer-events-none"
              style={{
                background: 'radial-gradient(circle, transparent 60%, rgba(34, 211, 238, 0.15) 70%, rgba(34, 211, 238, 0.05) 80%, transparent 90%)',
              }}
            />

            {/* Energy flow connections */}
            <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100">
              <defs>
                {/* Animated dash pattern */}
                <linearGradient id="lineGradientCyan" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#22d3ee" stopOpacity="0.8" />
                  <stop offset="100%" stopColor="#22d3ee" stopOpacity="0.1" />
                </linearGradient>
                <linearGradient id="lineGradientBlue" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.8" />
                  <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.1" />
                </linearGradient>
                <linearGradient id="lineGradientPurple" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#a855f7" stopOpacity="0.6" />
                  <stop offset="100%" stopColor="#a855f7" stopOpacity="0.1" />
                </linearGradient>
              </defs>

              {connections.map((conn, i) => {
                const color = getLineColor(conn.type || '');
                const gradientId = conn.type === 'federal' ? 'lineGradientBlue' :
                                   conn.type === 'international' ? 'lineGradientPurple' : 'lineGradientCyan';

                // Calculate curved path
                const midX = (conn.from.x + conn.to.x) / 2;
                const midY = (conn.from.y + conn.to.y) / 2 - 10;

                return (
                  <motion.path
                    key={i}
                    d={`M ${conn.from.x} ${conn.from.y} Q ${midX} ${midY} ${conn.to.x} ${conn.to.y}`}
                    fill="none"
                    stroke={`url(#${gradientId})`}
                    strokeWidth="0.4"
                    strokeLinecap="round"
                    initial={{ pathLength: 0, opacity: 0 }}
                    animate={{ pathLength: 1, opacity: 1 }}
                    transition={{
                      duration: 2,
                      delay: i * 0.2,
                      repeat: Infinity,
                      repeatType: 'loop',
                      repeatDelay: 3,
                    }}
                  />
                );
              })}
            </svg>

            {/* Energy nodes/markers */}
            {energyNodes.map((node, i) => (
              <motion.div
                key={node.id}
                className="absolute"
                style={{
                  left: `${node.x}%`,
                  top: `${node.y}%`,
                  transform: 'translate(-50%, -50%)',
                }}
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.5 + i * 0.1 }}
              >
                {node.primary ? (
                  // Colorado - main marker
                  <motion.button
                    onClick={handleColoradoClick}
                    onMouseEnter={() => setHoveredNode(node.id)}
                    onMouseLeave={() => setHoveredNode(null)}
                    className="relative cursor-pointer group"
                    whileHover={{ scale: 1.2 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    {/* Pulse rings */}
                    <motion.div
                      className="absolute inset-0 rounded-full bg-cyan-400"
                      animate={{ scale: [1, 2.5], opacity: [0.5, 0] }}
                      transition={{ duration: 2, repeat: Infinity }}
                      style={{ width: 20, height: 20, margin: -4 }}
                    />
                    <motion.div
                      className="absolute inset-0 rounded-full bg-cyan-400"
                      animate={{ scale: [1, 2], opacity: [0.3, 0] }}
                      transition={{ duration: 2, repeat: Infinity, delay: 0.5 }}
                      style={{ width: 20, height: 20, margin: -4 }}
                    />

                    {/* Main dot */}
                    <div className="w-3 h-3 rounded-full bg-cyan-400 shadow-lg shadow-cyan-400/50 group-hover:bg-cyan-300 transition-colors" />

                    {/* Label */}
                    <div className="absolute top-full left-1/2 -translate-x-1/2 mt-2 whitespace-nowrap">
                      <span className="text-xs font-medium text-cyan-400 bg-slate-900/80 px-2 py-1 rounded">
                        Colorado
                      </span>
                    </div>
                  </motion.button>
                ) : (
                  // Other nodes
                  <motion.div
                    className="relative"
                    onMouseEnter={() => setHoveredNode(node.id)}
                    onMouseLeave={() => setHoveredNode(null)}
                    whileHover={{ scale: 1.5 }}
                  >
                    <div
                      className="w-1.5 h-1.5 rounded-full"
                      style={{
                        backgroundColor: getLineColor(node.type || ''),
                        boxShadow: `0 0 8px ${getLineColor(node.type || '')}`,
                      }}
                    />

                    {/* Tooltip on hover */}
                    <AnimatePresence>
                      {hoveredNode === node.id && (
                        <motion.div
                          initial={{ opacity: 0, y: 5 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: 5 }}
                          className="absolute top-full left-1/2 -translate-x-1/2 mt-1 whitespace-nowrap z-10"
                        >
                          <span className="text-[10px] text-slate-300 bg-slate-800/90 px-2 py-0.5 rounded">
                            {node.name}
                          </span>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.div>
                )}
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.8 }}
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

      {/* Main content */}
      <AnimatePresence>
        {!isZooming && (
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            transition={{ delay: 0.8, duration: 0.8 }}
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

              {/* CTA Button */}
              <motion.button
                onClick={handleColoradoClick}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="group relative inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-2xl text-white font-medium text-lg shadow-2xl shadow-cyan-500/25 hover:shadow-cyan-500/40 transition-all duration-300"
              >
                <Globe2 className="w-5 h-5" />
                <span className="relative z-10">Explore Colorado Regulations</span>
                <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
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
