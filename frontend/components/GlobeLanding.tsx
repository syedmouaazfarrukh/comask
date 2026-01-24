'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Zap, Database, ChevronRight, Loader2, MapPin } from 'lucide-react';

interface GlobeLandingProps {
  onLocationSelect: (location: string) => void;
}

// Energy connection points with coordinates on the map (percentage based)
const energyNodes = [
  { id: 'colorado', name: 'Colorado', x: 21, y: 42, primary: true },
  { id: 'dc', name: 'Washington DC', x: 28, y: 43, type: 'federal' },
  { id: 'california', name: 'California', x: 14, y: 45, type: 'renewable' },
  { id: 'texas', name: 'Texas', x: 20, y: 52, type: 'energy' },
  { id: 'chicago', name: 'Chicago', x: 24, y: 40, type: 'grid' },
  { id: 'newyork', name: 'New York', x: 29, y: 41, type: 'exchange' },
  { id: 'seattle', name: 'Seattle', x: 14, y: 36, type: 'hydro' },
  { id: 'london', name: 'London', x: 47, y: 35, type: 'international' },
  { id: 'brussels', name: 'Brussels', x: 49, y: 36, type: 'international' },
  { id: 'tokyo', name: 'Tokyo', x: 85, y: 42, type: 'international' },
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
      }, 1500);
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
      {/* Subtle grid background */}
      <div
        className="absolute inset-0 opacity-10"
        style={{
          backgroundImage: `
            linear-gradient(rgba(34, 211, 238, 0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(34, 211, 238, 0.1) 1px, transparent 1px)
          `,
          backgroundSize: '50px 50px',
        }}
      />

      {/* Animated particles */}
      <div className="absolute inset-0 overflow-hidden">
        {[...Array(30)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-cyan-400/30 rounded-full"
            initial={{ opacity: 0, y: '100vh' }}
            animate={{
              opacity: [0, 0.5, 0],
              y: [window?.innerHeight || 800, -20],
              x: [0, Math.sin(i) * 50],
            }}
            transition={{
              duration: 8 + Math.random() * 4,
              repeat: Infinity,
              delay: Math.random() * 5,
              ease: 'linear',
            }}
            style={{
              left: `${Math.random() * 100}%`,
            }}
          />
        ))}
      </div>

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.8 }}
        className="absolute top-0 left-0 right-0 z-20 p-6 md:p-8"
      >
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-400 to-blue-500 flex items-center justify-center">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-light text-white tracking-wide">Comask</span>
          </div>
          <div className="hidden md:flex items-center gap-2 text-cyan-400/70 text-sm">
            <Database className="w-4 h-4" />
            <span>Energy Compliance Intelligence</span>
          </div>
        </div>
      </motion.div>

      {/* World Map Container */}
      <div className="absolute inset-0 flex items-center justify-center pt-16">
        <motion.div
          className="relative w-full max-w-6xl mx-auto px-4"
          animate={isZooming ? {
            scale: 2.5,
            x: '-30%',
            y: '20%',
            opacity: 0
          } : {
            scale: 1,
            x: 0,
            y: 0,
            opacity: 1
          }}
          transition={{ duration: 1.5, ease: 'easeInOut' }}
        >
          {/* SVG World Map */}
          <svg
            viewBox="0 0 100 50"
            className="w-full h-auto"
            style={{ maxHeight: '60vh' }}
          >
            <defs>
              {/* Gradients for connection lines */}
              <linearGradient id="lineGradientCyan" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#22d3ee" stopOpacity="0.9" />
                <stop offset="100%" stopColor="#22d3ee" stopOpacity="0.2" />
              </linearGradient>
              <linearGradient id="lineGradientBlue" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.9" />
                <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.2" />
              </linearGradient>
              <linearGradient id="lineGradientPurple" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#a855f7" stopOpacity="0.7" />
                <stop offset="100%" stopColor="#a855f7" stopOpacity="0.2" />
              </linearGradient>

              {/* Glow filter */}
              <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="0.3" result="coloredBlur"/>
                <feMerge>
                  <feMergeNode in="coloredBlur"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>

              {/* Pulse animation for Colorado */}
              <radialGradient id="pulseGradient">
                <stop offset="0%" stopColor="#22d3ee" stopOpacity="0.6" />
                <stop offset="100%" stopColor="#22d3ee" stopOpacity="0" />
              </radialGradient>
            </defs>

            {/* World Map Paths - Simplified continents */}
            <g className="opacity-40" fill="none" stroke="#22d3ee" strokeWidth="0.15">
              {/* North America */}
              <path d="M5,20 Q8,15 15,16 L22,18 Q28,20 32,25 L30,32 Q28,38 25,42 L22,48 Q18,52 15,50 L12,45 Q8,40 6,35 L5,28 Q4,24 5,20" />
              {/* South America */}
              <path d="M22,52 Q26,50 28,54 L30,60 Q32,68 30,75 L27,82 Q24,88 22,85 L20,78 Q18,70 19,62 L20,55 Q21,52 22,52" />
              {/* Europe */}
              <path d="M44,22 Q48,18 52,20 L56,22 Q60,25 58,30 L55,35 Q52,38 48,36 L45,32 Q42,28 44,22" />
              {/* Africa */}
              <path d="M46,38 Q50,35 54,38 L58,45 Q60,55 58,65 L55,72 Q52,78 48,75 L45,68 Q42,58 44,48 L46,38" />
              {/* Asia */}
              <path d="M58,18 Q65,14 75,16 L85,20 Q92,25 90,32 L88,40 Q85,48 78,45 L70,42 Q62,40 60,32 L58,25 Q57,20 58,18" />
              {/* Australia */}
              <path d="M82,58 Q88,55 92,58 L94,64 Q95,70 92,74 L88,76 Q84,75 82,70 L80,64 Q80,60 82,58" />
              {/* Greenland */}
              <path d="M32,10 Q36,8 40,10 L42,14 Q43,18 40,20 L36,18 Q33,16 32,12 L32,10" />
            </g>

            {/* Connection lines with animation */}
            {connections.map((conn, i) => {
              const gradientId = conn.type === 'federal' ? 'lineGradientBlue' :
                                 conn.type === 'international' ? 'lineGradientPurple' : 'lineGradientCyan';

              // Calculate curved path (arc)
              const dx = conn.to.x - conn.from.x;
              const dy = conn.to.y - conn.from.y;
              const distance = Math.sqrt(dx * dx + dy * dy);
              const curvature = Math.min(distance * 0.3, 15);
              const midX = (conn.from.x + conn.to.x) / 2;
              const midY = (conn.from.y + conn.to.y) / 2 - curvature;

              return (
                <g key={i}>
                  {/* Background line (static, dim) */}
                  <path
                    d={`M ${conn.from.x} ${conn.from.y} Q ${midX} ${midY} ${conn.to.x} ${conn.to.y}`}
                    fill="none"
                    stroke={getLineColor(conn.type || '')}
                    strokeWidth="0.08"
                    opacity="0.2"
                  />
                  {/* Animated line */}
                  <motion.path
                    d={`M ${conn.from.x} ${conn.from.y} Q ${midX} ${midY} ${conn.to.x} ${conn.to.y}`}
                    fill="none"
                    stroke={`url(#${gradientId})`}
                    strokeWidth="0.15"
                    strokeLinecap="round"
                    filter="url(#glow)"
                    initial={{ pathLength: 0, opacity: 0 }}
                    animate={{
                      pathLength: [0, 1, 1, 0],
                      opacity: [0, 1, 1, 0],
                    }}
                    transition={{
                      duration: 4,
                      delay: i * 0.3,
                      repeat: Infinity,
                      repeatDelay: 2,
                      times: [0, 0.4, 0.6, 1],
                    }}
                  />
                  {/* Moving dot along the line */}
                  <motion.circle
                    r="0.3"
                    fill={getLineColor(conn.type || '')}
                    filter="url(#glow)"
                    initial={{ opacity: 0 }}
                    animate={{
                      opacity: [0, 1, 1, 0],
                    }}
                    transition={{
                      duration: 4,
                      delay: i * 0.3,
                      repeat: Infinity,
                      repeatDelay: 2,
                      times: [0, 0.1, 0.9, 1],
                    }}
                  >
                    <animateMotion
                      dur="4s"
                      repeatCount="indefinite"
                      begin={`${i * 0.3}s`}
                      path={`M ${conn.from.x} ${conn.from.y} Q ${midX} ${midY} ${conn.to.x} ${conn.to.y}`}
                    />
                  </motion.circle>
                </g>
              );
            })}

            {/* Energy nodes */}
            {energyNodes.map((node, i) => (
              <g key={node.id}>
                {node.primary ? (
                  // Colorado - main interactive marker
                  <g
                    style={{ cursor: 'pointer' }}
                    onClick={handleColoradoClick}
                    onMouseEnter={() => setHoveredNode(node.id)}
                    onMouseLeave={() => setHoveredNode(null)}
                  >
                    {/* Pulse rings */}
                    <motion.circle
                      cx={node.x}
                      cy={node.y}
                      fill="url(#pulseGradient)"
                      initial={{ r: 0.5, opacity: 0.6 }}
                      animate={{ r: 3, opacity: 0 }}
                      transition={{ duration: 2, repeat: Infinity }}
                    />
                    <motion.circle
                      cx={node.x}
                      cy={node.y}
                      fill="url(#pulseGradient)"
                      initial={{ r: 0.5, opacity: 0.4 }}
                      animate={{ r: 2.5, opacity: 0 }}
                      transition={{ duration: 2, repeat: Infinity, delay: 0.5 }}
                    />
                    {/* Main dot */}
                    <motion.circle
                      cx={node.x}
                      cy={node.y}
                      r="0.8"
                      fill="#22d3ee"
                      filter="url(#glow)"
                      whileHover={{ scale: 1.3 }}
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: 0.5 }}
                    />
                    {/* Label */}
                    <motion.text
                      x={node.x}
                      y={node.y + 2.5}
                      textAnchor="middle"
                      fill="#22d3ee"
                      fontSize="1.8"
                      fontWeight="500"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.8 }}
                    >
                      Colorado
                    </motion.text>
                  </g>
                ) : (
                  // Other nodes
                  <g
                    onMouseEnter={() => setHoveredNode(node.id)}
                    onMouseLeave={() => setHoveredNode(null)}
                  >
                    <motion.circle
                      cx={node.x}
                      cy={node.y}
                      r="0.4"
                      fill={getLineColor(node.type || '')}
                      filter="url(#glow)"
                      initial={{ scale: 0, opacity: 0 }}
                      animate={{ scale: 1, opacity: 0.8 }}
                      transition={{ delay: 0.5 + i * 0.1 }}
                      whileHover={{ scale: 1.5 }}
                    />
                    {/* Tooltip */}
                    <AnimatePresence>
                      {hoveredNode === node.id && (
                        <motion.text
                          x={node.x}
                          y={node.y - 1.5}
                          textAnchor="middle"
                          fill="#94a3b8"
                          fontSize="1.2"
                          initial={{ opacity: 0, y: 0.5 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: 0.5 }}
                        >
                          {node.name}
                        </motion.text>
                      )}
                    </AnimatePresence>
                  </g>
                )}
              </g>
            ))}
          </svg>
        </motion.div>
      </div>

      {/* Bottom content */}
      <AnimatePresence>
        {!isZooming && (
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            transition={{ delay: 0.8, duration: 0.8 }}
            className="absolute bottom-0 left-0 right-0 z-20 p-6 md:p-8 pb-12 md:pb-16"
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
        className="absolute bottom-8 left-8 z-20 space-y-2 text-xs text-slate-500 hidden md:block"
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
