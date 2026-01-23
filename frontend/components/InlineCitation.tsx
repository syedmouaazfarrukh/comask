'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FileText, ExternalLink, X } from 'lucide-react';

export interface InlineCitationData {
  id: string;
  fact: string;
  source_index: number;
  source_title: string;
  source_excerpt: string;
  source_url?: string;
}

interface InlineCitationProps {
  citation: InlineCitationData;
  citationNumber: number;
}

export function InlineCitationTooltip({ citation, citationNumber }: InlineCitationProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [tooltipPosition, setTooltipPosition] = useState<'top' | 'bottom'>('bottom');
  const triggerRef = useRef<HTMLSpanElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen && triggerRef.current) {
      const rect = triggerRef.current.getBoundingClientRect();
      const spaceBelow = window.innerHeight - rect.bottom;
      const spaceAbove = rect.top;

      // If not enough space below (300px for tooltip), show above
      if (spaceBelow < 300 && spaceAbove > 300) {
        setTooltipPosition('top');
      } else {
        setTooltipPosition('bottom');
      }
    }
  }, [isOpen]);

  return (
    <span className="relative inline">
      <span
        ref={triggerRef}
        onClick={() => setIsOpen(!isOpen)}
        onMouseEnter={() => setIsOpen(true)}
        onMouseLeave={() => setIsOpen(false)}
        className="inline-flex items-center cursor-pointer group"
      >
        <span className="bg-blue-50 text-blue-800 border-b-2 border-blue-400 border-dotted px-0.5 rounded hover:bg-blue-100 hover:border-blue-600 transition-all duration-200">
          {citation.fact}
        </span>
        <span className="inline-flex items-center justify-center w-4 h-4 ml-0.5 text-[10px] font-semibold bg-blue-600 text-white rounded-full align-super group-hover:bg-blue-700 transition-colors">
          {citationNumber}
        </span>
      </span>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            ref={tooltipRef}
            initial={{ opacity: 0, y: tooltipPosition === 'bottom' ? -10 : 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: tooltipPosition === 'bottom' ? -10 : 10 }}
            transition={{ duration: 0.2 }}
            className={`absolute z-50 left-0 ${tooltipPosition === 'bottom' ? 'top-full mt-2' : 'bottom-full mb-2'} w-80 max-w-[90vw]`}
            onMouseEnter={() => setIsOpen(true)}
            onMouseLeave={() => setIsOpen(false)}
          >
            <div className="bg-white rounded-lg shadow-xl border border-gray-200 overflow-hidden">
              {/* Header */}
              <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-4 py-2 flex items-center justify-between">
                <div className="flex items-center gap-2 text-white">
                  <FileText className="w-4 h-4" />
                  <span className="text-sm font-medium">Source #{citationNumber}</span>
                </div>
                <button
                  onClick={(e) => { e.stopPropagation(); setIsOpen(false); }}
                  className="text-white/70 hover:text-white transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Content */}
              <div className="p-4 space-y-3">
                <div>
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Document</p>
                  <p className="text-sm font-medium text-gray-900">{citation.source_title}</p>
                </div>

                <div>
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Relevant Excerpt</p>
                  <p className="text-sm text-gray-700 bg-gray-50 p-2 rounded border-l-3 border-blue-500 italic">
                    &ldquo;{citation.source_excerpt.slice(0, 200)}...&rdquo;
                  </p>
                </div>

                {citation.source_url && citation.source_url !== '#' && (
                  <a
                    href={citation.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 text-sm text-blue-600 hover:text-blue-800 font-medium transition-colors"
                    onClick={(e) => e.stopPropagation()}
                  >
                    View full document
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                )}
              </div>

              {/* Arrow */}
              <div
                className={`absolute left-6 w-3 h-3 bg-white border-gray-200 transform rotate-45 ${
                  tooltipPosition === 'bottom'
                    ? '-top-1.5 border-l border-t'
                    : '-bottom-1.5 border-r border-b'
                }`}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </span>
  );
}

interface ParsedTextProps {
  text: string;
  inlineCitations: InlineCitationData[];
}

export function ParsedTextWithCitations({ text, inlineCitations }: ParsedTextProps) {
  // Parse the text to find [[cite-N:fact]] patterns and replace with components
  const citationPattern = /\[\[cite-(\d+):([^\]]+)\]\]/g;
  const parts: React.ReactNode[] = [];
  let lastIndex = 0;
  let match;
  let citationCounter = 0;

  // Create a map of citation IDs to citation data
  const citationMap = new Map(inlineCitations.map(c => [c.id, c]));

  while ((match = citationPattern.exec(text)) !== null) {
    // Add text before the citation
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index));
    }

    const citationId = `cite-${match[1]}`;
    const factText = match[2];
    const citation = citationMap.get(citationId);
    citationCounter++;

    if (citation) {
      parts.push(
        <InlineCitationTooltip
          key={`${citationId}-${match.index}`}
          citation={citation}
          citationNumber={citationCounter}
        />
      );
    } else {
      // If no matching citation found, just show the fact text
      parts.push(
        <span key={`fallback-${match.index}`} className="bg-yellow-50 text-yellow-800 px-0.5 rounded">
          {factText}
        </span>
      );
    }

    lastIndex = match.index + match[0].length;
  }

  // Add remaining text
  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }

  return <>{parts}</>;
}

export default InlineCitationTooltip;
