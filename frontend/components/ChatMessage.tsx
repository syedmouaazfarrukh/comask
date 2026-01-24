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
  isDark?: boolean;
}

// Custom component for rendering markdown with inline citations
function MarkdownWithCitations({
  content,
  inlineCitations,
  isDark = false
}: {
  content: string;
  inlineCitations: InlineCitationData[];
  isDark?: boolean;
}) {
  return (
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
          const processedChildren = processChildren(children, inlineCitations, isDark);
          return <p className="mb-3 last:mb-0">{processedChildren}</p>;
        },
        ul: ({ children }) => <ul className="list-disc list-outside mb-3 space-y-1 ml-6 pl-2">{children}</ul>,
        ol: ({ children }) => <ol className="list-decimal list-outside mb-3 space-y-1 ml-6 pl-2">{children}</ol>,
        li: ({ children }) => {
          const processedChildren = processChildren(children, inlineCitations, isDark);
          return <li className="ml-0">{processedChildren}</li>;
        },
        strong: ({ children }) => <strong className={`font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>{children}</strong>,
        em: ({ children }) => <em className="italic">{children}</em>,
        a: ({ href, children }) => (
          <a href={href} target="_blank" rel="noopener noreferrer" className={`underline ${isDark ? 'text-cyan-400 hover:text-cyan-300' : 'text-blue-600 hover:text-blue-700'}`}>
            {children}
          </a>
        ),
        code: ({ children }) => <code className={`px-1.5 py-0.5 rounded text-sm font-mono ${isDark ? 'bg-slate-700' : 'bg-gray-100'}`}>{children}</code>,
        blockquote: ({ children }) => <blockquote className={`border-l-4 pl-4 italic my-3 ${isDark ? 'border-slate-600' : 'border-gray-300'}`}>{children}</blockquote>,
        hr: () => <hr className={`my-4 ${isDark ? 'border-slate-700' : 'border-gray-200'}`} />,
      }}
    >
      {content}
    </ReactMarkdown>
  );
}

// Helper to process children and replace citation markers
function processChildren(children: React.ReactNode, inlineCitations: InlineCitationData[], isDark: boolean = false): React.ReactNode {
  if (!children) return children;

  if (typeof children === 'string') {
    if (children.includes('[[cite-')) {
      return <ParsedTextWithCitations text={children} inlineCitations={inlineCitations} isDark={isDark} />;
    }
    return children;
  }

  if (Array.isArray(children)) {
    return children.map((child, index) => {
      if (typeof child === 'string' && child.includes('[[cite-')) {
        return <ParsedTextWithCitations key={index} text={child} inlineCitations={inlineCitations} isDark={isDark} />;
      }
      return child;
    });
  }

  return children;
}

export default function ChatMessage({ message, onShowKnowledgeGraph, isDark = false }: ChatMessageProps) {
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
        className={`max-w-3xl rounded-2xl px-5 py-4 transition-colors duration-300 ${
          isUser
            ? isDark
              ? 'bg-cyan-600 text-white'
              : 'bg-blue-600 text-white'
            : isDark
              ? 'bg-slate-800 text-slate-100 border border-slate-700'
              : 'bg-white text-gray-900 border border-gray-200 shadow-sm'
        }`}
      >
        {isUser ? (
          <div className="whitespace-pre-wrap leading-relaxed">{message.content}</div>
        ) : (
          <div className={`prose prose-sm max-w-none leading-relaxed ${isDark ? 'prose-invert' : ''}`}>
            {hasInlineCitations ? (
              <MarkdownWithCitations
                content={message.content}
                inlineCitations={message.inline_citations || []}
                isDark={isDark}
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
                  strong: ({ children }) => <strong className={`font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>{children}</strong>,
                  em: ({ children }) => <em className="italic">{children}</em>,
                  a: ({ href, children }) => (
                    <a href={href} target="_blank" rel="noopener noreferrer" className={`underline ${isDark ? 'text-cyan-400 hover:text-cyan-300' : 'text-blue-600 hover:text-blue-700'}`}>
                      {children}
                    </a>
                  ),
                  code: ({ children }) => <code className={`px-1.5 py-0.5 rounded text-sm font-mono ${isDark ? 'bg-slate-700' : 'bg-gray-100'}`}>{children}</code>,
                  blockquote: ({ children }) => <blockquote className={`border-l-4 pl-4 italic my-3 ${isDark ? 'border-slate-600' : 'border-gray-300'}`}>{children}</blockquote>,
                  hr: () => <hr className={`my-4 ${isDark ? 'border-slate-700' : 'border-gray-200'}`} />,
                }}
              >
                {message.content}
              </ReactMarkdown>
            )}
          </div>
        )}

        {/* Inline Citations Legend */}
        {hasInlineCitations && (
          <div className={`mt-4 pt-3 border-t ${isDark ? 'border-slate-700' : 'border-gray-100'}`}>
            <p className={`text-xs flex items-center gap-1.5 ${isDark ? 'text-slate-400' : 'text-gray-500'}`}>
              <span className={`inline-flex items-center justify-center w-4 h-4 text-[9px] font-semibold rounded-full ${isDark ? 'bg-cyan-600 text-white' : 'bg-blue-600 text-white'}`}>
                ?
              </span>
              <span>Hover over <span className={`px-1 rounded border-b border-dotted ${isDark ? 'bg-cyan-900/50 text-cyan-300 border-cyan-500' : 'bg-blue-50 text-blue-800 border-blue-400'}`}>highlighted text</span> to see the source</span>
            </p>
          </div>
        )}

        {/* Knowledge Graph Button */}
        {hasRetrievalFlow && onShowKnowledgeGraph && (
          <div className="mt-3">
            <button
              onClick={() => onShowKnowledgeGraph(message.retrieval_flow!)}
              className={`inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
                isDark
                  ? 'text-cyan-400 bg-cyan-900/30 hover:bg-cyan-900/50'
                  : 'text-blue-700 bg-blue-50 hover:bg-blue-100'
              }`}
            >
              <Network className="w-4 h-4" />
              View Knowledge Graph
            </button>
          </div>
        )}

        {/* Sources Section */}
        {message.citations && message.citations.length > 0 && (
          <div className={`mt-4 pt-4 border-t ${isDark ? 'border-slate-700' : 'border-gray-200'}`}>
            <button
              onClick={() => setShowSources(!showSources)}
              className={`flex items-center gap-2 text-sm font-medium mb-2 transition-colors ${
                isDark ? 'text-slate-300 hover:text-white' : 'text-gray-700 hover:text-gray-900'
              }`}
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
                    className={`block p-3 rounded-lg transition-colors duration-150 group ${
                      isDark
                        ? 'bg-slate-700/50 hover:bg-slate-700'
                        : 'bg-gray-50 hover:bg-gray-100'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center ${
                        isDark ? 'bg-cyan-900/50' : 'bg-blue-100'
                      }`}>
                        <span className={`text-xs font-semibold ${isDark ? 'text-cyan-400' : 'text-blue-700'}`}>{index + 1}</span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <p className={`text-sm font-medium transition-colors truncate ${
                            isDark
                              ? 'text-slate-200 group-hover:text-cyan-400'
                              : 'text-gray-900 group-hover:text-blue-600'
                          }`}>
                            {citation.title}
                          </p>
                          <ExternalLink className={`w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0 ${
                            isDark ? 'text-slate-400' : 'text-gray-400'
                          }`} />
                        </div>
                        {citation.source && (
                          <p className={`text-xs mb-1 ${isDark ? 'text-cyan-400' : 'text-blue-600'}`}>{citation.source}</p>
                        )}
                        <p className={`text-xs line-clamp-2 ${isDark ? 'text-slate-400' : 'text-gray-600'}`}>{citation.excerpt}</p>
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
