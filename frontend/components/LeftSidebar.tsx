'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { X, MessageSquare, Settings, History, Plus } from 'lucide-react';

interface LeftSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  onNewChat: () => void;
  isDark?: boolean;
}

export default function LeftSidebar({ isOpen, onClose, onNewChat, isDark = false }: LeftSidebarProps) {
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
            className={`fixed inset-0 backdrop-blur-sm z-40 lg:hidden ${
              isDark ? 'bg-black/40' : 'bg-black/20'
            }`}
          />

          {/* Sidebar */}
          <motion.div
            initial={{ x: -320 }}
            animate={{ x: 0 }}
            exit={{ x: -320 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className={`fixed left-0 top-0 h-full w-80 z-50 flex flex-col shadow-xl lg:shadow-none transition-colors duration-300 ${
              isDark
                ? 'bg-slate-900 border-r border-slate-700'
                : 'bg-white border-r border-gray-200'
            }`}
          >
            {/* Header */}
            <div className={`flex items-center justify-between p-4 border-b ${
              isDark ? 'border-slate-700' : 'border-gray-200'
            }`}>
              <button
                onClick={onNewChat}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg border text-sm font-medium transition-colors ${
                  isDark
                    ? 'border-slate-700 hover:bg-slate-800 text-slate-300'
                    : 'border-gray-200 hover:bg-gray-50 text-gray-700'
                }`}
              >
                <Plus className="w-4 h-4" />
                New Chat
              </button>
              <button
                onClick={onClose}
                className={`p-2 rounded-lg transition-colors ${
                  isDark
                    ? 'hover:bg-slate-800 text-slate-400'
                    : 'hover:bg-gray-100 text-gray-500'
                }`}
                aria-label="Close sidebar"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-4">
              {/* Chat History */}
              <div className="mb-6">
                <h3 className={`text-xs font-semibold uppercase tracking-wider mb-2 px-2 ${
                  isDark ? 'text-slate-500' : 'text-gray-500'
                }`}>
                  Recent
                </h3>
                <div className="space-y-1">
                  {/* Mock chat history items */}
                  <button className={`w-full text-left px-3 py-2 rounded-lg transition-colors group ${
                    isDark ? 'hover:bg-slate-800' : 'hover:bg-gray-100'
                  }`}>
                    <div className="flex items-center gap-3">
                      <MessageSquare className={`w-4 h-4 ${
                        isDark
                          ? 'text-slate-500 group-hover:text-slate-300'
                          : 'text-gray-400 group-hover:text-gray-600'
                      }`} />
                      <span className={`text-sm truncate flex-1 ${
                        isDark ? 'text-slate-300' : 'text-gray-700'
                      }`}>
                        Solar panel regulations...
                      </span>
                    </div>
                  </button>
                  <button className={`w-full text-left px-3 py-2 rounded-lg transition-colors group ${
                    isDark ? 'hover:bg-slate-800' : 'hover:bg-gray-100'
                  }`}>
                    <div className="flex items-center gap-3">
                      <MessageSquare className={`w-4 h-4 ${
                        isDark
                          ? 'text-slate-500 group-hover:text-slate-300'
                          : 'text-gray-400 group-hover:text-gray-600'
                      }`} />
                      <span className={`text-sm truncate flex-1 ${
                        isDark ? 'text-slate-300' : 'text-gray-700'
                      }`}>
                        Net metering rules...
                      </span>
                    </div>
                  </button>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className={`border-t p-4 ${isDark ? 'border-slate-700' : 'border-gray-200'}`}>
              <button className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors text-sm ${
                isDark
                  ? 'hover:bg-slate-800 text-slate-300'
                  : 'hover:bg-gray-100 text-gray-700'
              }`}>
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
