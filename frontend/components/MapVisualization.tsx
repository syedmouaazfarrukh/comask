'use client';

import { motion } from 'framer-motion';
import { X } from 'lucide-react';
import ProcessingPipeline, { ProcessingStep } from './ProcessingPipeline';

interface ProcessingMetadata {
  intent_analysis?: {
    intent?: string;
    keywords?: string[];
  };
  source_search?: {
    sources_searched?: string[];
    sources_found?: number;
  };
  answer_generation?: {
    used_gpt_fallback?: boolean;
    sources_used?: number;
  };
}

interface DataSource {
  name: string;
  location: { lat: number; lng: number };
  color: string;
}

interface MapVisualizationProps {
  location: string;
  activeSources: string[];
  dataSources: DataSource[];
  processingStep?: ProcessingStep;
  processingMetadata?: ProcessingMetadata;
  onClose?: () => void;
  isComplete?: boolean;
}

export default function MapVisualization({ 
  location, 
  activeSources, 
  dataSources,
  processingStep = 'intent_analysis',
  processingMetadata,
  onClose,
  isComplete = false,
}: MapVisualizationProps) {

  return (
    <div className="h-full flex flex-col bg-white/95 backdrop-blur-sm">
      {/* Header */}
      <div className="border-b border-gray-200 px-4 py-3 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900">Processing Details</h3>
          <p className="text-xs text-gray-500">How we found your answer</p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Close"
          >
            <X className="w-4 h-4 text-gray-400" />
          </button>
        )}
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {/* Processing Pipeline */}
        <ProcessingPipeline
          currentStep={processingStep}
          processingMetadata={processingMetadata}
        />
      </div>
    </div>
  );
}

