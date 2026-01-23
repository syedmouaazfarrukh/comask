'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { X, MessageSquare, Settings, History, Plus } from 'lucide-react';

interface LeftSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  onNewChat: () => void;
}

export default function LeftSidebar({ isOpen, onClose, onNewChat }: LeftSidebarProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 lg:hidden"
          />
          
          {/* Sidebar */}
          <motion.div
            initial={{ x: -320 }}
            animate={{ x: 0 }}
            exit={{ x: -320 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed left-0 top-0 h-full w-80 bg-white border-r border-gray-200 z-50 flex flex-col shadow-xl lg:shadow-none"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <button
                onClick={onNewChat}
                className="flex items-center gap-2 px-3 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors text-sm font-medium text-gray-700"
              >
                <Plus className="w-4 h-4" />
                New Chat
              </button>
              <button
                onClick={onClose}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                aria-label="Close sidebar"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-4">
              {/* Chat History */}
              <div className="mb-6">
                <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 px-2">
                  Recent
                </h3>
                <div className="space-y-1">
                  {/* Mock chat history items */}
                  <button className="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors group">
                    <div className="flex items-center gap-3">
                      <MessageSquare className="w-4 h-4 text-gray-400 group-hover:text-gray-600" />
                      <span className="text-sm text-gray-700 truncate flex-1">
                        Solar panel regulations...
                      </span>
                    </div>
                  </button>
                  <button className="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors group">
                    <div className="flex items-center gap-3">
                      <MessageSquare className="w-4 h-4 text-gray-400 group-hover:text-gray-600" />
                      <span className="text-sm text-gray-700 truncate flex-1">
                        Net metering rules...
                      </span>
                    </div>
                  </button>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="border-t border-gray-200 p-4">
              <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors text-sm text-gray-700">
                <Settings className="w-4 h-4" />
                Settings
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

