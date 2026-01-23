'use client';

import { motion } from 'framer-motion';
import { FileText, ExternalLink } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Array<{
    title: string;
    url: string;
    excerpt: string;
  }>;
}

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

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
            <ReactMarkdown
              components={{
                h1: ({ children }) => <h1 className="text-xl font-semibold mb-3 mt-4 first:mt-0">{children}</h1>,
                h2: ({ children }) => <h2 className="text-lg font-semibold mb-2 mt-4 first:mt-0">{children}</h2>,
                h3: ({ children }) => <h3 className="text-base font-semibold mb-2 mt-3 first:mt-0">{children}</h3>,
                p: ({ children }) => {
                  // Don't render empty paragraphs (just whitespace or newlines)
                  if (typeof children === 'string' && !children.trim()) {
                    return null;
                  }
                  // Check if children is an array with only whitespace
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
          </div>
        )}

        {message.citations && message.citations.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200 space-y-3">
            <p className="text-sm font-medium text-gray-700 mb-2">Sources:</p>
            {message.citations.map((citation, index) => (
              <a
                key={index}
                href={citation.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-150 group"
              >
                <div className="flex items-start gap-3">
                  <FileText className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="text-sm font-medium text-gray-900 group-hover:text-blue-600 transition-colors">
                        {citation.title}
                      </p>
                      <ExternalLink className="w-3 h-3 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                    <p className="text-xs text-gray-600 line-clamp-2">{citation.excerpt}</p>
                  </div>
                </div>
              </a>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}

