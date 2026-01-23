'use client';

import { motion } from 'framer-motion';
import { X } from 'lucide-react';
import ProcessingPipeline, { ProcessingStep } from './ProcessingPipeline';

interface TopDocument {
  title: string;
  source: string;
  relevance_score: number;
  excerpt_preview?: string;
}

interface ProcessingMetadata {
  intent_analysis?: {
    intent?: string;
    intent_description?: string;
    keywords?: string[];
    entities?: string[];
    confidence?: string;
    is_followup?: boolean;
    processing_time_ms?: number;
  };
  source_search?: {
    search_method?: string;
    embeddings_used?: boolean;
    sources_searched?: string[];
    sources_found?: number;
    top_documents?: TopDocument[];
    average_relevance?: number;
    processing_time_ms?: number;
  };
  answer_generation?: {
    used_gpt_fallback?: boolean;
    sources_used?: number;
    inline_citations_count?: number;
    model_used?: string;
    tokens_used?: number;
    confidence?: string;
    processing_time_ms?: number;
  };
  validation?: {
    completed?: boolean;
    issues?: string[];
    is_valid?: boolean;
    processing_time_ms?: number;
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
  totalProcessingTime?: number;
  onClose?: () => void;
  isComplete?: boolean;
}

export default function MapVisualization({
  location,
  activeSources,
  dataSources,
  processingStep = 'intent_analysis',
  processingMetadata,
  totalProcessingTime,
  onClose,
  isComplete = false,
}: MapVisualizationProps) {

  return (
    <div className="h-full flex flex-col bg-white/95 backdrop-blur-sm">
      {/* Header */}
      <div className="border-b border-gray-200 px-4 py-3 flex items-center justify-between bg-gradient-to-r from-purple-50/50 to-cyan-50/50">
        <div>
          <h3 className="text-sm font-semibold text-gray-900">Processing Insights</h3>
          <p className="text-xs text-gray-500">Detailed view of how we found your answer</p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="p-1.5 hover:bg-white/50 rounded-lg transition-colors"
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
          totalProcessingTime={totalProcessingTime}
        />
      </div>
    </div>
  );
}

