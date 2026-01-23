'use client';

import { motion } from 'framer-motion';
import { CheckCircle2, Circle, Loader2, Brain, Search, Sparkles, MessageSquare, AlertCircle } from 'lucide-react';

export type ProcessingStep = 
  | 'intent_analysis'
  | 'source_search'
  | 'answer_generation'
  | 'complete';

interface ProcessingPipelineProps {
  currentStep: ProcessingStep;
  processingMetadata?: {
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
  };
}

const steps = [
  {
    id: 'intent_analysis' as ProcessingStep,
    label: 'Understanding Your Question',
    description: 'Analyzing what you\'re asking for',
    icon: Brain,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
  },
  {
    id: 'source_search' as ProcessingStep,
    label: 'Searching Official Sources',
    description: 'Looking through Colorado energy regulations',
    icon: Search,
    color: 'text-cyan-600',
    bgColor: 'bg-cyan-50',
  },
  {
    id: 'answer_generation' as ProcessingStep,
    label: 'Generating Answer',
    description: 'Creating your response',
    icon: Sparkles,
    color: 'text-indigo-600',
    bgColor: 'bg-indigo-50',
  },
  {
    id: 'complete' as ProcessingStep,
    label: 'Complete',
    description: 'Answer ready',
    icon: MessageSquare,
    color: 'text-green-600',
    bgColor: 'bg-green-50',
  },
];

export default function ProcessingPipeline({
  currentStep,
  processingMetadata,
}: ProcessingPipelineProps) {
  const getStepIndex = (step: ProcessingStep) => {
    return steps.findIndex(s => s.id === step);
  };

  const currentStepIndex = getStepIndex(currentStep);

  return (
    <div className="space-y-4">

      <div className="space-y-3">
        {steps.map((step, index) => {
          const Icon = step.icon;
          const isActive = index <= currentStepIndex;
          const isCurrent = step.id === currentStep;
          const isComplete = index < currentStepIndex;

          return (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: isActive ? 1 : 0.4, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className={`relative flex items-start gap-3 p-3 rounded-lg transition-all duration-200 ${
                isCurrent && step.id !== 'complete' ? `${step.bgColor} border-2 border-current` : 
                step.id === 'complete' && currentStep === 'complete' ? 'bg-green-50 border-2 border-green-200' :
                isComplete ? 'bg-gray-50 border border-gray-200' : 'bg-white/50 border border-gray-200'
              }`}
            >
              {/* Step Icon */}
              <div className={`flex-shrink-0 ${step.color}`}>
                {isComplete || (step.id === 'complete' && currentStep === 'complete') ? (
                  <CheckCircle2 className="w-5 h-5" />
                ) : isCurrent && step.id !== 'complete' ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Circle className="w-5 h-5 opacity-30" />
                )}
              </div>

              {/* Step Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <Icon className={`w-4 h-4 ${step.color} flex-shrink-0`} />
                  <h4 className={`text-sm font-medium ${isActive ? 'text-gray-900' : 'text-gray-400'}`}>
                    {step.label}
                  </h4>
                </div>
                <p className={`text-xs ${isActive ? 'text-gray-600' : 'text-gray-400'}`}>
                  {step.description}
                </p>

                {/* Step-specific details */}
                {(isCurrent || isComplete) && processingMetadata && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="mt-2 space-y-2"
                  >
                    {step.id === 'intent_analysis' && processingMetadata.intent_analysis && (
                      <div className="space-y-1">
                        <p className="text-xs text-gray-600 font-medium">
                          ✓ Identified: {processingMetadata.intent_analysis.intent || 'General query'}
                        </p>
                        {processingMetadata.intent_analysis.keywords && processingMetadata.intent_analysis.keywords.length > 0 && (
                          <p className="text-xs text-gray-500">
                            Keywords: {processingMetadata.intent_analysis.keywords.slice(0, 3).join(', ')}
                            {processingMetadata.intent_analysis.keywords.length > 3 && '...'}
                          </p>
                        )}
                      </div>
                    )}
                    {step.id === 'source_search' && processingMetadata.source_search && (
                      <div className="space-y-1">
                        {processingMetadata.source_search.sources_searched && processingMetadata.source_search.sources_searched.length > 0 ? (
                          <>
                            <p className="text-xs text-gray-600 font-medium">
                              ✓ Searched {processingMetadata.source_search.sources_searched.length} source{processingMetadata.source_search.sources_searched.length !== 1 ? 's' : ''}:
                            </p>
                            <ul className="text-xs text-gray-500 list-disc list-inside ml-2 space-y-0.5">
                              {processingMetadata.source_search.sources_searched.map((source, idx) => (
                                <li key={idx}>{source}</li>
                              ))}
                            </ul>
                            {processingMetadata.source_search.sources_found !== undefined && (
                              processingMetadata.source_search.sources_found === 0 ? (
                                <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded-md">
                                  <div className="flex items-start gap-2">
                                    <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
                                    <div className="flex-1">
                                      <p className="text-xs text-red-800 font-medium">
                                        ⚠️ No relevant sources found
                                      </p>
                                      <p className="text-xs text-red-700 mt-0.5">
                                        Database search returned empty. Answer will be generated using GPT with public sources.
                                      </p>
                                    </div>
                                  </div>
                                </div>
                              ) : (
                                <p className="text-xs text-green-600 font-medium mt-1">
                                  ✓ Found {processingMetadata.source_search.sources_found} relevant source{processingMetadata.source_search.sources_found !== 1 ? 's' : ''}
                                </p>
                              )
                            )}
                          </>
                        ) : (
                          <p className="text-xs text-gray-500">Searching official sources...</p>
                        )}
                      </div>
                    )}
                    {step.id === 'answer_generation' && processingMetadata.answer_generation && (
                      <div className="space-y-1">
                        {processingMetadata.answer_generation.used_gpt_fallback ? (
                          <div className="p-2 bg-amber-50 border border-amber-200 rounded-md">
                            <div className="flex items-start gap-2">
                              <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
                              <div className="flex-1">
                                <p className="text-xs text-amber-800 font-medium">
                                  Used GPT for additional context
                                </p>
                                <p className="text-xs text-amber-700 mt-0.5">
                                  No relevant sources found in database, so we used GPT to gather information from public sources and internet research.
                                </p>
                              </div>
                            </div>
                          </div>
                        ) : processingMetadata.answer_generation.sources_used !== undefined && processingMetadata.answer_generation.sources_used > 0 ? (
                          <p className="text-xs text-gray-600">
                            ✓ Generated answer using {processingMetadata.answer_generation.sources_used} verified source{processingMetadata.answer_generation.sources_used !== 1 ? 's' : ''}
                          </p>
                        ) : (
                          <p className="text-xs text-gray-500">Generating answer...</p>
                        )}
                      </div>
                    )}
                    {step.id === 'complete' && (
                      <p className="text-xs text-green-600 font-medium">
                        ✓ Answer ready
                      </p>
                    )}
                  </motion.div>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>

    </div>
  );
}

