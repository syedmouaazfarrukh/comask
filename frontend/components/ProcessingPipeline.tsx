'use client';

import { motion } from 'framer-motion';
import {
  CheckCircle2,
  Circle,
  Loader2,
  Brain,
  Search,
  Sparkles,
  MessageSquare,
  AlertCircle,
  FileText,
  Database,
  Zap,
  Clock,
  Tag,
  ChevronDown,
  ChevronUp,
  Shield,
  TrendingUp
} from 'lucide-react';
import { useState } from 'react';

export type ProcessingStep =
  | 'intent_analysis'
  | 'source_search'
  | 'answer_generation'
  | 'complete';

interface TopDocument {
  title: string;
  source: string;
  relevance_score: number;
  excerpt_preview?: string;
}

interface ProcessingPipelineProps {
  currentStep: ProcessingStep;
  processingMetadata?: {
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
  };
  totalProcessingTime?: number;
  isDark?: boolean;
}

const steps = [
  {
    id: 'intent_analysis' as ProcessingStep,
    label: 'Understanding Your Question',
    description: 'Analyzing what you\'re asking for',
    icon: Brain,
    color: 'text-purple-600',
    darkColor: 'text-purple-400',
    bgColor: 'bg-purple-50',
    darkBgColor: 'bg-purple-900/30',
    borderColor: 'border-purple-200',
    darkBorderColor: 'border-purple-700',
  },
  {
    id: 'source_search' as ProcessingStep,
    label: 'Searching Knowledge Base',
    description: 'Finding relevant documents and regulations',
    icon: Database,
    color: 'text-cyan-600',
    darkColor: 'text-cyan-400',
    bgColor: 'bg-cyan-50',
    darkBgColor: 'bg-cyan-900/30',
    borderColor: 'border-cyan-200',
    darkBorderColor: 'border-cyan-700',
  },
  {
    id: 'answer_generation' as ProcessingStep,
    label: 'Generating Answer',
    description: 'Creating a comprehensive response with citations',
    icon: Sparkles,
    color: 'text-indigo-600',
    darkColor: 'text-indigo-400',
    bgColor: 'bg-indigo-50',
    darkBgColor: 'bg-indigo-900/30',
    borderColor: 'border-indigo-200',
    darkBorderColor: 'border-indigo-700',
  },
  {
    id: 'complete' as ProcessingStep,
    label: 'Complete',
    description: 'Answer ready with sources',
    icon: CheckCircle2,
    color: 'text-green-600',
    darkColor: 'text-green-400',
    bgColor: 'bg-green-50',
    darkBgColor: 'bg-green-900/30',
    borderColor: 'border-green-200',
    darkBorderColor: 'border-green-700',
  },
];

// Helper component for expandable document list
function DocumentList({ documents, isDark = false }: { documents: TopDocument[]; isDark?: boolean }) {
  const [expanded, setExpanded] = useState(false);
  const displayDocs = expanded ? documents : documents.slice(0, 2);

  return (
    <div className="mt-2 space-y-2">
      {displayDocs.map((doc, idx) => (
        <div key={idx} className={`p-2 rounded-md border shadow-sm ${
          isDark ? 'bg-slate-800 border-slate-700' : 'bg-white border-gray-100'
        }`}>
          <div className="flex items-start gap-2">
            <FileText className={`w-3.5 h-3.5 flex-shrink-0 mt-0.5 ${isDark ? 'text-cyan-400' : 'text-cyan-600'}`} />
            <div className="flex-1 min-w-0">
              <p className={`text-xs font-medium truncate ${isDark ? 'text-slate-200' : 'text-gray-800'}`}>{doc.title}</p>
              <div className="flex items-center gap-2 mt-0.5">
                <span className={`text-[10px] ${isDark ? 'text-slate-400' : 'text-gray-500'}`}>{doc.source}</span>
                <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${
                  isDark ? 'bg-green-900/50 text-green-400' : 'bg-green-100 text-green-700'
                }`}>
                  {doc.relevance_score}% match
                </span>
              </div>
              {doc.excerpt_preview && (
                <p className={`text-[10px] mt-1 line-clamp-2 italic ${isDark ? 'text-slate-500' : 'text-gray-500'}`}>
                  "{doc.excerpt_preview}"
                </p>
              )}
            </div>
          </div>
        </div>
      ))}
      {documents.length > 2 && (
        <button
          onClick={() => setExpanded(!expanded)}
          className={`flex items-center gap-1 text-xs font-medium ${
            isDark ? 'text-cyan-400 hover:text-cyan-300' : 'text-cyan-600 hover:text-cyan-700'
          }`}
        >
          {expanded ? (
            <>
              <ChevronUp className="w-3 h-3" />
              Show less
            </>
          ) : (
            <>
              <ChevronDown className="w-3 h-3" />
              Show {documents.length - 2} more documents
            </>
          )}
        </button>
      )}
    </div>
  );
}

// Helper component for confidence badge
function ConfidenceBadge({ confidence, isDark = false }: { confidence: string; isDark?: boolean }) {
  const colors = isDark ? {
    high: 'bg-green-900/50 text-green-400 border-green-700',
    medium: 'bg-amber-900/50 text-amber-400 border-amber-700',
    low: 'bg-red-900/50 text-red-400 border-red-700',
  } : {
    high: 'bg-green-100 text-green-700 border-green-200',
    medium: 'bg-amber-100 text-amber-700 border-amber-200',
    low: 'bg-red-100 text-red-700 border-red-200',
  };
  const color = colors[confidence as keyof typeof colors] || colors.medium;

  return (
    <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium border ${color}`}>
      {confidence.charAt(0).toUpperCase() + confidence.slice(1)} Confidence
    </span>
  );
}

// Helper component for timing display
function TimingDisplay({ ms, isDark = false }: { ms: number; isDark?: boolean }) {
  if (!ms) return null;
  const seconds = (ms / 1000).toFixed(1);
  return (
    <span className={`flex items-center gap-1 text-[10px] ${isDark ? 'text-slate-500' : 'text-gray-400'}`}>
      <Clock className="w-3 h-3" />
      {seconds}s
    </span>
  );
}

export default function ProcessingPipeline({
  currentStep,
  processingMetadata,
  totalProcessingTime,
  isDark = false,
}: ProcessingPipelineProps) {
  const getStepIndex = (step: ProcessingStep) => {
    return steps.findIndex(s => s.id === step);
  };

  const currentStepIndex = getStepIndex(currentStep);

  return (
    <div className="space-y-3">
      {steps.map((step, index) => {
        const Icon = step.icon;
        const isActive = index <= currentStepIndex;
        const isCurrent = step.id === currentStep;
        const isComplete = index < currentStepIndex;

        return (
          <motion.div
            key={step.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: isActive ? 1 : 0.4, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            className={`relative rounded-xl transition-all duration-200 overflow-hidden ${
              isCurrent && step.id !== 'complete'
                ? isDark
                  ? `${step.darkBgColor} border-2 ${step.darkBorderColor} shadow-sm`
                  : `${step.bgColor} border-2 ${step.borderColor} shadow-sm`
                : step.id === 'complete' && currentStep === 'complete'
                  ? isDark
                    ? 'bg-green-900/30 border-2 border-green-700 shadow-sm'
                    : 'bg-green-50 border-2 border-green-200 shadow-sm'
                  : isComplete
                    ? isDark
                      ? 'bg-slate-800/50 border border-slate-700'
                      : 'bg-gray-50/80 border border-gray-200'
                    : isDark
                      ? 'bg-slate-800/30 border border-slate-700'
                      : 'bg-white/50 border border-gray-200'
            }`}
          >
            {/* Main step content */}
            <div className="p-3">
              <div className="flex items-start gap-3">
                {/* Step Icon */}
                <div className={`flex-shrink-0 p-2 rounded-lg ${
                  isComplete || (step.id === 'complete' && currentStep === 'complete')
                    ? isDark ? 'bg-green-900/50' : 'bg-green-100'
                    : isDark ? step.darkBgColor : step.bgColor
                }`}>
                  {isComplete || (step.id === 'complete' && currentStep === 'complete') ? (
                    <CheckCircle2 className={`w-4 h-4 ${isDark ? 'text-green-400' : 'text-green-600'}`} />
                  ) : isCurrent && step.id !== 'complete' ? (
                    <Loader2 className={`w-4 h-4 ${isDark ? step.darkColor : step.color} animate-spin`} />
                  ) : (
                    <Icon className={`w-4 h-4 ${isActive ? (isDark ? step.darkColor : step.color) : (isDark ? 'text-slate-600' : 'text-gray-300')}`} />
                  )}
                </div>

                {/* Step Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <h4 className={`text-sm font-semibold ${
                      isActive ? (isDark ? 'text-white' : 'text-gray-900') : (isDark ? 'text-slate-500' : 'text-gray-400')
                    }`}>
                      {step.label}
                    </h4>
                    {/* Show timing when complete */}
                    {isComplete && processingMetadata && (
                      <TimingDisplay
                        isDark={isDark}
                        ms={
                          step.id === 'intent_analysis' ? processingMetadata.intent_analysis?.processing_time_ms || 0 :
                          step.id === 'source_search' ? processingMetadata.source_search?.processing_time_ms || 0 :
                          step.id === 'answer_generation' ? processingMetadata.answer_generation?.processing_time_ms || 0 : 0
                        }
                      />
                    )}
                  </div>
                  <p className={`text-xs mt-0.5 ${
                    isActive ? (isDark ? 'text-slate-400' : 'text-gray-600') : (isDark ? 'text-slate-600' : 'text-gray-400')
                  }`}>
                    {step.description}
                  </p>
                </div>
              </div>

              {/* Step-specific detailed content */}
              {(isCurrent || isComplete) && processingMetadata && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className={`mt-3 pt-3 border-t ${isDark ? 'border-slate-700' : 'border-gray-100'}`}
                >
                  {/* Intent Analysis Details */}
                  {step.id === 'intent_analysis' && processingMetadata.intent_analysis && (
                    <div className="space-y-3">
                      {/* Intent type */}
                      <div className="flex items-start gap-2">
                        <Tag className={`w-3.5 h-3.5 flex-shrink-0 mt-0.5 ${isDark ? 'text-purple-400' : 'text-purple-500'}`} />
                        <div>
                          <p className={`text-xs font-medium ${isDark ? 'text-slate-200' : 'text-gray-800'}`}>
                            Query Type: {processingMetadata.intent_analysis.intent?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </p>
                          {processingMetadata.intent_analysis.intent_description && (
                            <p className={`text-[10px] mt-0.5 ${isDark ? 'text-slate-400' : 'text-gray-500'}`}>
                              {processingMetadata.intent_analysis.intent_description}
                            </p>
                          )}
                        </div>
                      </div>

                      {/* Keywords */}
                      {processingMetadata.intent_analysis.keywords && processingMetadata.intent_analysis.keywords.length > 0 && (
                        <div>
                          <p className={`text-[10px] font-medium uppercase tracking-wider mb-1 ${isDark ? 'text-slate-500' : 'text-gray-500'}`}>
                            Key Terms Identified
                          </p>
                          <div className="flex flex-wrap gap-1">
                            {processingMetadata.intent_analysis.keywords.map((keyword, idx) => (
                              <span
                                key={idx}
                                className={`text-[10px] px-2 py-0.5 rounded-full ${
                                  isDark ? 'bg-purple-900/50 text-purple-300' : 'bg-purple-100 text-purple-700'
                                }`}
                              >
                                {keyword}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Follow-up indicator */}
                      {processingMetadata.intent_analysis.is_followup && (
                        <div className={`flex items-center gap-1.5 text-xs ${isDark ? 'text-purple-400' : 'text-purple-600'}`}>
                          <Zap className="w-3 h-3" />
                          <span>Recognized as follow-up to previous question</span>
                        </div>
                      )}

                      {/* Confidence */}
                      {processingMetadata.intent_analysis.confidence && (
                        <div className="flex items-center gap-2">
                          <span className={`text-[10px] ${isDark ? 'text-slate-400' : 'text-gray-500'}`}>Understanding:</span>
                          <ConfidenceBadge confidence={processingMetadata.intent_analysis.confidence} isDark={isDark} />
                        </div>
                      )}
                    </div>
                  )}

                  {/* Source Search Details */}
                  {step.id === 'source_search' && processingMetadata.source_search && (
                    <div className="space-y-3">
                      {/* Search method */}
                      <div className="flex items-center gap-2">
                        <div className={`flex items-center gap-1.5 text-xs px-2 py-1 rounded-md ${
                          processingMetadata.source_search.embeddings_used
                            ? isDark ? 'bg-cyan-900/50 text-cyan-400' : 'bg-cyan-100 text-cyan-700'
                            : isDark ? 'bg-slate-700 text-slate-300' : 'bg-gray-100 text-gray-600'
                        }`}>
                          {processingMetadata.source_search.embeddings_used ? (
                            <>
                              <TrendingUp className="w-3 h-3" />
                              <span className="font-medium">Semantic Vector Search</span>
                            </>
                          ) : (
                            <>
                              <Search className="w-3 h-3" />
                              <span className="font-medium">Keyword Search</span>
                            </>
                          )}
                        </div>
                      </div>

                      {/* Sources searched */}
                      {processingMetadata.source_search.sources_searched && processingMetadata.source_search.sources_searched.length > 0 && (
                        <div>
                          <p className={`text-[10px] font-medium uppercase tracking-wider mb-1 ${isDark ? 'text-slate-500' : 'text-gray-500'}`}>
                            Databases Searched
                          </p>
                          <div className="grid grid-cols-1 gap-1">
                            {processingMetadata.source_search.sources_searched.map((source, idx) => (
                              <div key={idx} className={`flex items-center gap-2 text-xs ${isDark ? 'text-slate-300' : 'text-gray-700'}`}>
                                <Database className={`w-3 h-3 ${isDark ? 'text-cyan-400' : 'text-cyan-500'}`} />
                                <span>{source}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Results summary */}
                      <div className={`flex items-center gap-3 p-2 rounded-lg border ${
                        isDark ? 'bg-slate-800 border-slate-700' : 'bg-white border-gray-100'
                      }`}>
                        <div className="text-center">
                          <p className={`text-lg font-bold ${isDark ? 'text-cyan-400' : 'text-cyan-600'}`}>
                            {processingMetadata.source_search.sources_found || 0}
                          </p>
                          <p className={`text-[10px] ${isDark ? 'text-slate-400' : 'text-gray-500'}`}>Documents Found</p>
                        </div>
                        {processingMetadata.source_search.average_relevance !== undefined && processingMetadata.source_search.average_relevance > 0 && (
                          <div className={`text-center border-l pl-3 ${isDark ? 'border-slate-700' : 'border-gray-200'}`}>
                            <p className={`text-lg font-bold ${isDark ? 'text-green-400' : 'text-green-600'}`}>
                              {processingMetadata.source_search.average_relevance}%
                            </p>
                            <p className={`text-[10px] ${isDark ? 'text-slate-400' : 'text-gray-500'}`}>Avg. Relevance</p>
                          </div>
                        )}
                      </div>

                      {/* Top documents */}
                      {processingMetadata.source_search.top_documents && processingMetadata.source_search.top_documents.length > 0 && (
                        <div>
                          <p className={`text-[10px] font-medium uppercase tracking-wider mb-2 ${isDark ? 'text-slate-500' : 'text-gray-500'}`}>
                            Most Relevant Documents
                          </p>
                          <DocumentList documents={processingMetadata.source_search.top_documents} isDark={isDark} />
                        </div>
                      )}

                      {/* No results warning */}
                      {processingMetadata.source_search.sources_found === 0 && (
                        <div className={`p-2 rounded-lg border ${
                          isDark ? 'bg-amber-900/30 border-amber-700' : 'bg-amber-50 border-amber-200'
                        }`}>
                          <div className="flex items-start gap-2">
                            <AlertCircle className={`w-4 h-4 flex-shrink-0 ${isDark ? 'text-amber-400' : 'text-amber-600'}`} />
                            <div>
                              <p className={`text-xs font-medium ${isDark ? 'text-amber-300' : 'text-amber-800'}`}>No matching documents found</p>
                              <p className={`text-[10px] mt-0.5 ${isDark ? 'text-amber-400' : 'text-amber-700'}`}>
                                Will use AI knowledge to generate response with general information.
                              </p>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Answer Generation Details */}
                  {step.id === 'answer_generation' && processingMetadata.answer_generation && (
                    <div className="space-y-3">
                      {/* GPT Fallback warning */}
                      {processingMetadata.answer_generation.used_gpt_fallback ? (
                        <div className={`p-2 rounded-lg border ${
                          isDark ? 'bg-amber-900/30 border-amber-700' : 'bg-amber-50 border-amber-200'
                        }`}>
                          <div className="flex items-start gap-2">
                            <AlertCircle className={`w-4 h-4 flex-shrink-0 ${isDark ? 'text-amber-400' : 'text-amber-600'}`} />
                            <div>
                              <p className={`text-xs font-medium ${isDark ? 'text-amber-300' : 'text-amber-800'}`}>Generated from AI Knowledge</p>
                              <p className={`text-[10px] mt-0.5 ${isDark ? 'text-amber-400' : 'text-amber-700'}`}>
                                No database documents matched. Response based on AI's training data about Colorado energy regulations.
                              </p>
                            </div>
                          </div>
                        </div>
                      ) : (
                        <>
                          {/* Generation stats */}
                          <div className="grid grid-cols-2 gap-2">
                            <div className={`p-2 rounded-lg border text-center ${
                              isDark ? 'bg-slate-800 border-slate-700' : 'bg-white border-gray-100'
                            }`}>
                              <p className={`text-lg font-bold ${isDark ? 'text-indigo-400' : 'text-indigo-600'}`}>
                                {processingMetadata.answer_generation.sources_used || 0}
                              </p>
                              <p className={`text-[10px] ${isDark ? 'text-slate-400' : 'text-gray-500'}`}>Sources Used</p>
                            </div>
                            <div className={`p-2 rounded-lg border text-center ${
                              isDark ? 'bg-slate-800 border-slate-700' : 'bg-white border-gray-100'
                            }`}>
                              <p className={`text-lg font-bold ${isDark ? 'text-blue-400' : 'text-blue-600'}`}>
                                {processingMetadata.answer_generation.inline_citations_count || 0}
                              </p>
                              <p className={`text-[10px] ${isDark ? 'text-slate-400' : 'text-gray-500'}`}>Inline Citations</p>
                            </div>
                          </div>

                          {/* Confidence */}
                          {processingMetadata.answer_generation.confidence && (
                            <div className="flex items-center gap-2">
                              <Shield className={`w-3.5 h-3.5 ${isDark ? 'text-indigo-400' : 'text-indigo-500'}`} />
                              <span className={`text-xs ${isDark ? 'text-slate-300' : 'text-gray-600'}`}>Answer Confidence:</span>
                              <ConfidenceBadge confidence={processingMetadata.answer_generation.confidence} isDark={isDark} />
                            </div>
                          )}
                        </>
                      )}

                      {/* Model info */}
                      {processingMetadata.answer_generation.model_used && (
                        <div className={`flex items-center gap-2 text-[10px] ${isDark ? 'text-slate-500' : 'text-gray-400'}`}>
                          <Sparkles className="w-3 h-3" />
                          <span>Model: {processingMetadata.answer_generation.model_used}</span>
                          {processingMetadata.answer_generation.tokens_used && processingMetadata.answer_generation.tokens_used > 0 && (
                            <span>| {processingMetadata.answer_generation.tokens_used.toLocaleString()} tokens</span>
                          )}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Complete Details */}
                  {step.id === 'complete' && currentStep === 'complete' && (
                    <div className="space-y-2">
                      <div className={`flex items-center gap-2 ${isDark ? 'text-green-400' : 'text-green-700'}`}>
                        <CheckCircle2 className="w-4 h-4" />
                        <span className="text-sm font-medium">Answer ready with verified sources</span>
                      </div>

                      {/* Validation status */}
                      {processingMetadata?.validation && (
                        <div className={`flex items-center gap-2 text-xs ${
                          processingMetadata.validation.is_valid
                            ? isDark ? 'text-green-400' : 'text-green-600'
                            : isDark ? 'text-amber-400' : 'text-amber-600'
                        }`}>
                          <Shield className="w-3.5 h-3.5" />
                          <span>
                            {processingMetadata.validation.is_valid
                              ? 'Response validated successfully'
                              : `Validation completed with ${processingMetadata.validation.issues?.length || 0} notes`}
                          </span>
                        </div>
                      )}

                      {/* Total time */}
                      {totalProcessingTime && (
                        <div className={`flex items-center gap-2 text-xs pt-2 border-t ${
                          isDark ? 'text-slate-400 border-slate-700' : 'text-gray-500 border-gray-100'
                        }`}>
                          <Clock className="w-3.5 h-3.5" />
                          <span>Total processing time: {(totalProcessingTime / 1000).toFixed(1)}s</span>
                        </div>
                      )}
                    </div>
                  )}
                </motion.div>
              )}
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
