'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { FileText, ExternalLink, Network, ChevronDown, ChevronUp } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { ParsedTextWithCitations, InlineCitationData } from './InlineCitation';

interface Citation {
  title: string;
  url: string;
  excerpt: string;
  source?: string;
  published_date?: string;
  relevance_score?: number;
}

interface RetrievalFlowNode {
  id: string;
  type: string;
  label: string;
  metadata?: Record<string, unknown>;
}

interface RetrievalFlowEdge {
  source: string;
  target: string;
  label?: string;
  relevance_score?: number;
}

interface RetrievalFlow {
  nodes: RetrievalFlowNode[];
  edges: RetrievalFlowEdge[];
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  inline_citations?: InlineCitationData[];
  retrieval_flow?: RetrievalFlow;
}

interface ChatMessageProps {
  message: Message;
  onShowKnowledgeGraph?: (flow: RetrievalFlow) => void;
}

// Custom component for rendering markdown with inline citations
function MarkdownWithCitations({
  content,
  inlineCitations
}: {
  content: string;
  inlineCitations: InlineCitationData[];
}) {
  return (
    <ReactMarkdown
      components={{
        h1: ({ children }) => <h1 className="text-xl font-semibold mb-3 mt-4 first:mt-0">{children}</h1>,
        h2: ({ children }) => <h2 className="text-lg font-semibold mb-2 mt-4 first:mt-0">{children}</h2>,
        h3: ({ children }) => <h3 className="text-base font-semibold mb-2 mt-3 first:mt-0">{children}</h3>,
        p: ({ children }) => {
          // Don't render empty paragraphs
          if (typeof children === 'string' && !children.trim()) {
            return null;
          }
          if (Array.isArray(children) && children.every(child =>
            typeof child === 'string' && !child.trim()
          )) {
            return null;
          }

          // Parse children for inline citations
          const processedChildren = processChildren(children, inlineCitations);

          return <p className="mb-3 last:mb-0">{processedChildren}</p>;
        },
        ul: ({ children }) => <ul className="list-disc list-outside mb-3 space-y-1 ml-6 pl-2">{children}</ul>,
        ol: ({ children }) => <ol className="list-decimal list-outside mb-3 space-y-1 ml-6 pl-2">{children}</ol>,
        li: ({ children }) => {
          const processedChildren = processChildren(children, inlineCitations);
          return <li className="ml-0">{processedChildren}</li>;
        },
        strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
        em: ({ children }) => <em className="italic">{children}</em>,
        a: ({ href, children }) => (
          <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-700 underline">
            {children}
          </a>
        ),
        code: ({ children }) => <code className="bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono">{children}</code>,
        blockquote: ({ children }) => <blockquote className="border-l-4 border-gray-300 pl-4 italic my-3">{children}</blockquote>,
        hr: () => <hr className="my-4 border-gray-200" />,
      }}
    >
      {content}
    </ReactMarkdown>
  );
}

// Helper to process children and replace citation markers
function processChildren(children: React.ReactNode, inlineCitations: InlineCitationData[]): React.ReactNode {
  if (!children) return children;

  if (typeof children === 'string') {
    // Check if there are any citation patterns
    if (children.includes('[[cite-')) {
      return <ParsedTextWithCitations text={children} inlineCitations={inlineCitations} />;
    }
    return children;
  }

  if (Array.isArray(children)) {
    return children.map((child, index) => {
      if (typeof child === 'string' && child.includes('[[cite-')) {
        return <ParsedTextWithCitations key={index} text={child} inlineCitations={inlineCitations} />;
      }
      return child;
    });
  }

  return children;
}

export default function ChatMessage({ message, onShowKnowledgeGraph }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const [showSources, setShowSources] = useState(true);
  const hasInlineCitations = message.inline_citations && message.inline_citations.length > 0;
  const hasRetrievalFlow = message.retrieval_flow && message.retrieval_flow.nodes.length > 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`max-w-3xl rounded-2xl px-5 py-4 ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-white text-gray-900 border border-gray-200 shadow-sm'
        }`}
      >
        {isUser ? (
          <div className="whitespace-pre-wrap leading-relaxed">{message.content}</div>
        ) : (
          <div className="prose prose-sm max-w-none leading-relaxed">
            {hasInlineCitations ? (
              <MarkdownWithCitations
                content={message.content}
                inlineCitations={message.inline_citations || []}
              />
            ) : (
              <ReactMarkdown
                components={{
                  h1: ({ children }) => <h1 className="text-xl font-semibold mb-3 mt-4 first:mt-0">{children}</h1>,
                  h2: ({ children }) => <h2 className="text-lg font-semibold mb-2 mt-4 first:mt-0">{children}</h2>,
                  h3: ({ children }) => <h3 className="text-base font-semibold mb-2 mt-3 first:mt-0">{children}</h3>,
                  p: ({ children }) => {
                    if (typeof children === 'string' && !children.trim()) {
                      return null;
                    }
                    if (Array.isArray(children) && children.every(child =>
                      typeof child === 'string' && !child.trim()
                    )) {
                      return null;
                    }
                    return <p className="mb-3 last:mb-0">{children}</p>;
                  },
                  ul: ({ children }) => <ul className="list-disc list-outside mb-3 space-y-1 ml-6 pl-2">{children}</ul>,
                  ol: ({ children }) => <ol className="list-decimal list-outside mb-3 space-y-1 ml-6 pl-2">{children}</ol>,
                  li: ({ children }) => <li className="ml-0">{children}</li>,
                  strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
                  em: ({ children }) => <em className="italic">{children}</em>,
                  a: ({ href, children }) => (
                    <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-700 underline">
                      {children}
                    </a>
                  ),
                  code: ({ children }) => <code className="bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono">{children}</code>,
                  blockquote: ({ children }) => <blockquote className="border-l-4 border-gray-300 pl-4 italic my-3">{children}</blockquote>,
                  hr: () => <hr className="my-4 border-gray-200" />,
                }}
              >
                {message.content}
              </ReactMarkdown>
            )}
          </div>
        )}

        {/* Inline Citations Legend */}
        {hasInlineCitations && (
          <div className="mt-4 pt-3 border-t border-gray-100">
            <p className="text-xs text-gray-500 flex items-center gap-1.5">
              <span className="inline-flex items-center justify-center w-4 h-4 text-[9px] font-semibold bg-blue-600 text-white rounded-full">
                ?
              </span>
              <span>Hover over <span className="bg-blue-50 text-blue-800 px-1 rounded border-b border-dotted border-blue-400">highlighted text</span> to see the source</span>
            </p>
          </div>
        )}

        {/* Knowledge Graph Button */}
        {hasRetrievalFlow && onShowKnowledgeGraph && (
          <div className="mt-3">
            <button
              onClick={() => onShowKnowledgeGraph(message.retrieval_flow!)}
              className="inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-blue-700 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
            >
              <Network className="w-4 h-4" />
              View Knowledge Graph
            </button>
          </div>
        )}

        {/* Sources Section */}
        {message.citations && message.citations.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <button
              onClick={() => setShowSources(!showSources)}
              className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2 hover:text-gray-900 transition-colors"
            >
              <span>Sources ({message.citations.length})</span>
              {showSources ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>

            {showSources && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="space-y-3"
              >
                {message.citations.map((citation, index) => (
                  <a
                    key={index}
                    href={citation.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-150 group"
                  >
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0 w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-xs font-semibold text-blue-700">{index + 1}</span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <p className="text-sm font-medium text-gray-900 group-hover:text-blue-600 transition-colors truncate">
                            {citation.title}
                          </p>
                          <ExternalLink className="w-3 h-3 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
                        </div>
                        {citation.source && (
                          <p className="text-xs text-blue-600 mb-1">{citation.source}</p>
                        )}
                        <p className="text-xs text-gray-600 line-clamp-2">{citation.excerpt}</p>
                      </div>
                    </div>
                  </a>
                ))}
              </motion.div>
            )}
          </div>
        )}
      </div>
    </motion.div>
  );
}
