'use client';

import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';

export default function ThinkingIndicator() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center gap-3 text-gray-600"
    >
      <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
      <span className="text-sm font-light">Analyzing regulations...</span>
    </motion.div>
  );
}

