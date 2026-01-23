'use client';

import { motion } from 'framer-motion';

export default function AnimatedGradientBlobs() {
  const blobs = [
    {
      id: 1,
      color: 'from-emerald-400/30 to-teal-500/30',
      size: 'w-96 h-96',
      position: { top: '10%', left: '10%' },
      duration: 20,
      delay: 0,
    },
    {
      id: 2,
      color: 'from-cyan-400/30 to-blue-500/30',
      size: 'w-80 h-80',
      position: { top: '60%', right: '15%' },
      duration: 25,
      delay: 5,
    },
    {
      id: 3,
      color: 'from-green-400/25 to-emerald-500/25',
      size: 'w-72 h-72',
      position: { bottom: '20%', left: '20%' },
      duration: 30,
      delay: 10,
    },
    {
      id: 4,
      color: 'from-teal-400/30 to-cyan-500/30',
      size: 'w-64 h-64',
      position: { top: '30%', right: '30%' },
      duration: 22,
      delay: 2,
    },
  ];

  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none -z-10">
      {blobs.map((blob) => (
        <motion.div
          key={blob.id}
          className={`absolute ${blob.size} rounded-full bg-gradient-to-br ${blob.color} blur-3xl`}
          style={{
            top: blob.position.top,
            left: blob.position.left,
            right: blob.position.right,
            bottom: blob.position.bottom,
          }}
          animate={{
            scale: [1, 1.2, 0.9, 1.1, 1],
            x: [0, 50, -30, 40, 0],
            y: [0, -40, 30, -20, 0],
            opacity: [0.3, 0.5, 0.4, 0.6, 0.3],
          }}
          transition={{
            duration: blob.duration,
            repeat: Infinity,
            ease: 'easeInOut',
            delay: blob.delay,
          }}
        />
      ))}
    </div>
  );
}

