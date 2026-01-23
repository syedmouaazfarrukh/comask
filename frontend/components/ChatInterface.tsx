'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, MapPin, Menu, PanelRight, RefreshCw } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ChatMessage from './ChatMessage';
import ThinkingIndicator from './ThinkingIndicator';
import MapVisualization from './MapVisualization';
import LeftSidebar from './LeftSidebar';
import KnowledgeGraph from './KnowledgeGraph';
import { ProcessingStep } from './ProcessingPipeline';
import { submitQuery, createConversation, deleteConversation, type QueryResponse } from '@/lib/api';

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
  const [hasActiveQuery, setHasActiveQuery] = useState(false); // Track if there's an active query
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
      // Update processing step as we go
      setProcessingStep('intent_analysis');
      
      // Create conversation if needed
      let currentConversationId = conversationId;
      if (!currentConversationId) {
        const convResponse = await createConversation(location.toLowerCase());
        currentConversationId = convResponse.conversation_id;
        setConversationId(currentConversationId);
      }
      
      // Simulate step progression
      setTimeout(() => setProcessingStep('source_search'), 500);
      setTimeout(() => setProcessingStep('answer_generation'), 1500);
      
      // Call the real backend API
      const response: QueryResponse = await submitQuery({
        question,
        location: location.toLowerCase(),
        conversation_id: currentConversationId,
      });
      
      // Update conversation ID from response if provided
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      // Update processing metadata from response
      const metadata = response.metadata || {};
      
      // Extract processing steps metadata
      const processingSteps = metadata.processing_steps || {};
      
      // Set processing metadata with all the detailed info
      setProcessingMetadata({
        intent_analysis: processingSteps.intent_analysis,
        source_search: processingSteps.source_search,
        answer_generation: processingSteps.answer_generation,
        validation: processingSteps.validation,
        totalProcessingTime: metadata.total_processing_time_ms || response.processing_time_ms,
      });
      
      // Update active sources from actual sources searched
      if (metadata.sources_searched && Array.isArray(metadata.sources_searched)) {
        setActiveSources(metadata.sources_searched);
      }
      
      // Update processing step to complete
      setProcessingStep('complete');

      // Convert backend response to frontend message format
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
      
      // Show error message to user
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
    setHasActiveQuery(false); // Once closed, can't reopen until new question
  };

  const handleNewChat = async () => {
    // Delete current conversation if exists
    if (conversationId) {
      try {
        await deleteConversation(conversationId);
      } catch (error) {
        console.error('Failed to delete conversation:', error);
      }
    }
    
    // Reset state
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
    <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-teal-50 relative z-20">
      {/* Left Sidebar */}
      <LeftSidebar 
        isOpen={leftSidebarOpen} 
        onClose={() => setLeftSidebarOpen(false)}
        onNewChat={handleNewChat}
      />

      {/* Header */}
      <div className="border-b border-gray-200 bg-white/80 backdrop-blur-sm px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center gap-3">
          {/* Left Sidebar Toggle */}
          <button
            onClick={() => setLeftSidebarOpen(!leftSidebarOpen)}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Toggle sidebar"
          >
            <Menu className="w-5 h-5 text-gray-600" />
          </button>
          
          <MapPin className="w-5 h-5 text-blue-600" />
          <h1 className="text-xl font-light text-gray-900">Colorado Energy Regulations</h1>
          
          <div className="ml-auto flex items-center gap-2">
            {/* Refresh/New Chat Button */}
            {conversationId && (
              <button
                onClick={handleNewChat}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                aria-label="Start new conversation"
                title="Start new conversation"
              >
                <RefreshCw className="w-5 h-5 text-gray-600" />
              </button>
            )}
            
            {/* Right Sidebar Toggle - Only show if there's an active query */}
            {hasActiveQuery && (
              <button
                onClick={() => setShowRightSidebar(!showRightSidebar)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                aria-label="Toggle processing sidebar"
              >
                <PanelRight className={`w-5 h-5 text-gray-600 ${showRightSidebar ? 'text-blue-600' : ''}`} />
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
                  />
                ))}
              </AnimatePresence>

              {isThinking && (
                <div className="space-y-4">
                  <ThinkingIndicator />
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-200 bg-white/80 backdrop-blur-sm px-4 py-4">
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
                    className="w-full px-4 py-3 pr-12 bg-white border border-gray-200 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-400"
                    style={{
                      maxHeight: '200px',
                      minHeight: '48px',
                    }}
                  />
                </div>
                <button
                  type="submit"
                  disabled={!input.trim() || isThinking}
                  className="p-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200 flex items-center justify-center"
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
              className="border-l border-gray-200 overflow-hidden"
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
          />
        )}
      </AnimatePresence>
    </div>
  );
}

