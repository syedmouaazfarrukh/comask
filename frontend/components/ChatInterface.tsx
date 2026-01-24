'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, MapPin, Menu, PanelRight, RefreshCw, Sun, Moon } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ChatMessage from './ChatMessage';
import ThinkingIndicator from './ThinkingIndicator';
import MapVisualization from './MapVisualization';
import LeftSidebar from './LeftSidebar';
import KnowledgeGraph from './KnowledgeGraph';
import { ProcessingStep } from './ProcessingPipeline';
import { submitQuery, createConversation, deleteConversation, type QueryResponse } from '@/lib/api';
import { useTheme } from '@/contexts/ThemeContext';

// Inline citation data structure
interface InlineCitationData {
  id: string;
  fact: string;
  source_index: number;
  source_title: string;
  source_excerpt: string;
  source_url?: string;
}

// Retrieval flow structures for knowledge graph
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
  citations?: Array<{
    title: string;
    url: string;
    excerpt: string;
  }>;
  inline_citations?: InlineCitationData[];
  retrieval_flow?: RetrievalFlow;
}

interface ChatInterfaceProps {
  location: string;
}

// Mock data sources for Colorado
const coloradoDataSources = [
  { name: 'Colorado Public Utilities Commission', location: { lat: 39.7392, lng: -104.9903 }, color: '#0ea5e9' },
  { name: 'Colorado Energy Office', location: { lat: 39.7392, lng: -104.9903 }, color: '#0284c7' },
  { name: 'Colorado State Legislature', location: { lat: 39.7392, lng: -104.9903 }, color: '#0369a1' },
];

export default function ChatInterface({ location }: ChatInterfaceProps) {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === 'dark';

  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: `Hello! I'm here to help you with Colorado energy regulations. Ask me anything about compliance, rules, or policies.`,
    },
  ]);
  const [input, setInput] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [activeSources, setActiveSources] = useState<string[]>([]);
  const [showRightSidebar, setShowRightSidebar] = useState(false);
  const [leftSidebarOpen, setLeftSidebarOpen] = useState(false);
  const [hasActiveQuery, setHasActiveQuery] = useState(false);
  const [processingStep, setProcessingStep] = useState<ProcessingStep>('intent_analysis');
  const [processingMetadata, setProcessingMetadata] = useState<any>(null);
  const [showKnowledgeGraph, setShowKnowledgeGraph] = useState(false);
  const [currentRetrievalFlow, setCurrentRetrievalFlow] = useState<RetrievalFlow | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isThinking]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isThinking) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const question = input.trim();
    setInput('');
    setIsThinking(true);
    setShowRightSidebar(true);
    setHasActiveQuery(true);
    setActiveSources([]);
    setProcessingStep('intent_analysis');
    setProcessingMetadata(null);

    try {
      setProcessingStep('intent_analysis');

      let currentConversationId = conversationId;
      if (!currentConversationId) {
        const convResponse = await createConversation(location.toLowerCase());
        currentConversationId = convResponse.conversation_id;
        setConversationId(currentConversationId);
      }

      setTimeout(() => setProcessingStep('source_search'), 500);
      setTimeout(() => setProcessingStep('answer_generation'), 1500);

      const response: QueryResponse = await submitQuery({
        question,
        location: location.toLowerCase(),
        conversation_id: currentConversationId,
      });

      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      const metadata = response.metadata || {};
      const processingSteps = metadata.processing_steps || {};

      setProcessingMetadata({
        intent_analysis: processingSteps.intent_analysis,
        source_search: processingSteps.source_search,
        answer_generation: processingSteps.answer_generation,
        validation: processingSteps.validation,
        totalProcessingTime: metadata.total_processing_time_ms || response.processing_time_ms,
      });

      if (metadata.sources_searched && Array.isArray(metadata.sources_searched)) {
        setActiveSources(metadata.sources_searched);
      }

      setProcessingStep('complete');

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        citations: response.citations.map(cit => ({
          title: cit.title,
          url: cit.url || '#',
          excerpt: cit.excerpt,
        })),
        inline_citations: response.inline_citations,
        retrieval_flow: response.retrieval_flow,
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setIsThinking(false);
    } catch (error) {
      console.error('Error submitting query:', error);

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `I'm sorry, I encountered an error while processing your question. Please try again or check your connection to the backend server.\n\nError: ${error instanceof Error ? error.message : 'Unknown error'}`,
      };

      setMessages((prev) => [...prev, errorMessage]);
      setIsThinking(false);
      setProcessingStep('complete');
    }
  };

  const handleCloseRightSidebar = () => {
    setShowRightSidebar(false);
    setHasActiveQuery(false);
  };

  const handleNewChat = async () => {
    if (conversationId) {
      try {
        await deleteConversation(conversationId);
      } catch (error) {
        console.error('Failed to delete conversation:', error);
      }
    }

    setMessages([
      {
        id: '1',
        role: 'assistant',
        content: `Hello! I'm here to help you with Colorado energy regulations. Ask me anything about compliance, rules, or policies.`,
      },
    ]);
    setConversationId(null);
    setShowRightSidebar(false);
    setHasActiveQuery(false);
    setLeftSidebarOpen(false);
  };

  const handleShowKnowledgeGraph = (flow: RetrievalFlow) => {
    setCurrentRetrievalFlow(flow);
    setShowKnowledgeGraph(true);
  };

  return (
    <div className={`flex flex-col h-screen relative z-20 transition-colors duration-300 ${
      isDark
        ? 'bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950'
        : 'bg-gradient-to-br from-blue-50 via-cyan-50 to-teal-50'
    }`}>
      {/* Left Sidebar */}
      <LeftSidebar
        isOpen={leftSidebarOpen}
        onClose={() => setLeftSidebarOpen(false)}
        onNewChat={handleNewChat}
        isDark={isDark}
      />

      {/* Header */}
      <div className={`border-b px-6 py-4 transition-colors duration-300 ${
        isDark
          ? 'border-slate-700 bg-slate-900/80 backdrop-blur-sm'
          : 'border-gray-200 bg-white/80 backdrop-blur-sm'
      }`}>
        <div className="max-w-4xl mx-auto flex items-center gap-3">
          {/* Left Sidebar Toggle */}
          <button
            onClick={() => setLeftSidebarOpen(!leftSidebarOpen)}
            className={`p-2 rounded-lg transition-colors ${
              isDark
                ? 'hover:bg-slate-800 text-slate-400 hover:text-slate-200'
                : 'hover:bg-gray-100 text-gray-600'
            }`}
            aria-label="Toggle sidebar"
          >
            <Menu className="w-5 h-5" />
          </button>

          <img
            src={isDark ? '/logow.png' : '/logob.png'}
            alt="Comask"
            className="h-10 w-auto"
          />

          <div className="ml-auto flex items-center gap-2">
            {/* Theme Toggle */}
            <motion.button
              onClick={toggleTheme}
              className={`p-2 rounded-lg transition-colors ${
                isDark
                  ? 'hover:bg-slate-800 text-slate-400 hover:text-yellow-400'
                  : 'hover:bg-gray-100 text-gray-600 hover:text-slate-800'
              }`}
              aria-label="Toggle theme"
              title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
              whileTap={{ scale: 0.95 }}
            >
              <AnimatePresence mode="wait">
                {isDark ? (
                  <motion.div
                    key="sun"
                    initial={{ rotate: -90, opacity: 0 }}
                    animate={{ rotate: 0, opacity: 1 }}
                    exit={{ rotate: 90, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <Sun className="w-5 h-5" />
                  </motion.div>
                ) : (
                  <motion.div
                    key="moon"
                    initial={{ rotate: 90, opacity: 0 }}
                    animate={{ rotate: 0, opacity: 1 }}
                    exit={{ rotate: -90, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <Moon className="w-5 h-5" />
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.button>

            {/* Refresh/New Chat Button */}
            {conversationId && (
              <button
                onClick={handleNewChat}
                className={`p-2 rounded-lg transition-colors ${
                  isDark
                    ? 'hover:bg-slate-800 text-slate-400 hover:text-slate-200'
                    : 'hover:bg-gray-100 text-gray-600'
                }`}
                aria-label="Start new conversation"
                title="Start new conversation"
              >
                <RefreshCw className="w-5 h-5" />
              </button>
            )}

            {/* Right Sidebar Toggle */}
            {hasActiveQuery && (
              <button
                onClick={() => setShowRightSidebar(!showRightSidebar)}
                className={`p-2 rounded-lg transition-colors ${
                  isDark
                    ? 'hover:bg-slate-800 text-slate-400 hover:text-slate-200'
                    : 'hover:bg-gray-100 text-gray-600'
                } ${showRightSidebar ? (isDark ? 'text-cyan-400' : 'text-blue-600') : ''}`}
                aria-label="Toggle processing sidebar"
              >
                <PanelRight className="w-5 h-5" />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Chat Messages */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto px-4 py-6">
            <div className="max-w-4xl mx-auto space-y-6">
              <AnimatePresence>
                {messages.map((message) => (
                  <ChatMessage
                    key={message.id}
                    message={message}
                    onShowKnowledgeGraph={handleShowKnowledgeGraph}
                    isDark={isDark}
                  />
                ))}
              </AnimatePresence>

              {isThinking && (
                <div className="space-y-4">
                  <ThinkingIndicator isDark={isDark} />
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Input Area */}
          <div className={`border-t px-4 py-4 transition-colors duration-300 ${
            isDark
              ? 'border-slate-700 bg-slate-900/80 backdrop-blur-sm'
              : 'border-gray-200 bg-white/80 backdrop-blur-sm'
          }`}>
            <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
              <div className="flex items-end gap-3">
                <div className="flex-1 relative">
                  <textarea
                    ref={inputRef}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSubmit(e);
                      }
                    }}
                    placeholder="Ask about Colorado energy regulations..."
                    rows={1}
                    className={`w-full px-4 py-3 pr-12 rounded-xl resize-none focus:outline-none focus:ring-2 transition-colors duration-300 ${
                      isDark
                        ? 'bg-slate-800 border border-slate-700 text-white placeholder-slate-500 focus:ring-cyan-500 focus:border-transparent'
                        : 'bg-white border border-gray-200 text-gray-900 placeholder-gray-400 focus:ring-blue-500 focus:border-transparent'
                    }`}
                    style={{
                      maxHeight: '200px',
                      minHeight: '48px',
                    }}
                  />
                </div>
                <button
                  type="submit"
                  disabled={!input.trim() || isThinking}
                  className={`p-3 rounded-xl transition-colors duration-200 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed ${
                    isDark
                      ? 'bg-cyan-600 text-white hover:bg-cyan-500'
                      : 'bg-blue-600 text-white hover:bg-blue-700'
                  }`}
                >
                  {isThinking ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Send className="w-5 h-5" />
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Map Visualization Sidebar (Right) */}
        <AnimatePresence>
          {showRightSidebar && (
            <motion.div
              initial={{ width: 0, opacity: 0 }}
              animate={{ width: 384, opacity: 1 }}
              exit={{ width: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className={`border-l overflow-hidden ${
                isDark ? 'border-slate-700' : 'border-gray-200'
              }`}
            >
              <MapVisualization
                location={location}
                activeSources={activeSources}
                dataSources={coloradoDataSources}
                processingStep={processingStep}
                processingMetadata={processingMetadata}
                totalProcessingTime={processingMetadata?.totalProcessingTime}
                onClose={handleCloseRightSidebar}
                isComplete={processingStep === 'complete'}
                isDark={isDark}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Knowledge Graph Modal */}
      <AnimatePresence>
        {showKnowledgeGraph && currentRetrievalFlow && (
          <KnowledgeGraph
            retrievalFlow={currentRetrievalFlow}
            onClose={() => setShowKnowledgeGraph(false)}
            isDark={isDark}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
