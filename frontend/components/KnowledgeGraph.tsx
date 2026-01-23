'use client';

import { useCallback, useMemo, useState } from 'react';
import {
  ReactFlow,
  Node,
  Edge,
  Controls,
  Background,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
  NodeTypes,
  Handle,
  Position,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { X, FileText, MessageSquare, CheckCircle, ExternalLink } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// Types from API
interface GraphNode {
  id: string;
  type: string;
  data: Record<string, any>;
  position: { x: number; y: number };
}

interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: string;
  label?: string;
  data?: Record<string, any>;
  animated?: boolean;
}

interface SourceGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

interface KnowledgeGraphProps {
  graph: SourceGraph;
  onClose: () => void;
}

// Custom node styles based on type
const nodeStyles = {
  answer: {
    background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
    color: '#ffffff',
    border: '2px solid #1e40af',
  },
  claim: {
    background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
    color: '#1e293b',
    border: '2px solid #cbd5e1',
  },
  source: {
    background: 'linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%)',
    color: '#065f46',
    border: '2px solid #10b981',
  },
  section: {
    background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',
    color: '#92400e',
    border: '2px solid #f59e0b',
  },
};

// Authority level colors
const authorityColors: Record<string, { bg: string; text: string; border: string }> = {
  FEDERAL: { bg: '#1e40af', text: '#ffffff', border: '#1e3a8a' },
  STATE: { bg: '#059669', text: '#ffffff', border: '#047857' },
  REGIONAL: { bg: '#7c3aed', text: '#ffffff', border: '#6d28d9' },
  UTILITY: { bg: '#ea580c', text: '#ffffff', border: '#c2410c' },
  '1': { bg: '#1e40af', text: '#ffffff', border: '#1e3a8a' },
  '2': { bg: '#059669', text: '#ffffff', border: '#047857' },
  '3': { bg: '#7c3aed', text: '#ffffff', border: '#6d28d9' },
  '4': { bg: '#ea580c', text: '#ffffff', border: '#c2410c' },
};

// Custom Answer Node
function AnswerNode({ data }: { data: any }) {
  return (
    <div
      className="px-4 py-3 rounded-xl shadow-lg min-w-[200px] max-w-[300px]"
      style={nodeStyles.answer}
    >
      <Handle type="source" position={Position.Bottom} className="!bg-blue-300" />
      <div className="flex items-center gap-2 mb-2">
        <MessageSquare className="w-5 h-5" />
        <span className="font-semibold">Answer</span>
      </div>
      <p className="text-sm opacity-90 line-clamp-3">{data.preview || data.label}</p>
    </div>
  );
}

// Custom Claim Node
function ClaimNode({ data }: { data: any }) {
  return (
    <div
      className="px-4 py-3 rounded-lg shadow-md min-w-[180px] max-w-[250px]"
      style={nodeStyles.claim}
    >
      <Handle type="target" position={Position.Top} className="!bg-slate-400" />
      <Handle type="source" position={Position.Bottom} className="!bg-slate-400" />
      <div className="flex items-center gap-2 mb-1">
        <CheckCircle className="w-4 h-4 text-slate-500" />
        <span className="font-medium text-sm">{data.label}</span>
      </div>
      <p className="text-xs text-slate-600 line-clamp-2">{data.preview || data.text}</p>
    </div>
  );
}

// Custom Source Node
function SourceNode({ data, selected }: { data: any; selected: boolean }) {
  const authority = data.authority_level || data.style?.authority;
  const colors = authorityColors[authority] || { bg: '#059669', text: '#ffffff', border: '#047857' };

  return (
    <div
      className={`px-4 py-3 rounded-lg shadow-md min-w-[180px] max-w-[280px] transition-all ${
        selected ? 'ring-2 ring-blue-500 ring-offset-2' : ''
      }`}
      style={{
        backgroundColor: colors.bg,
        color: colors.text,
        border: `2px solid ${colors.border}`,
      }}
    >
      <Handle type="target" position={Position.Top} className="!bg-white/50" />
      <Handle type="source" position={Position.Bottom} className="!bg-white/50" />
      <div className="flex items-center gap-2 mb-2">
        <FileText className="w-4 h-4" />
        <span className="font-medium text-sm truncate">{data.label}</span>
      </div>
      {data.citation && (
        <p className="text-xs opacity-80 mb-1">{data.citation}</p>
      )}
      {data.excerpt && (
        <p className="text-xs opacity-70 line-clamp-2">{data.excerpt}</p>
      )}
      {data.similarity_score && (
        <div className="mt-2 text-xs opacity-80">
          Match: {Math.round(data.similarity_score * 100)}%
        </div>
      )}
    </div>
  );
}

// Custom Section Node
function SectionNode({ data }: { data: any }) {
  return (
    <div
      className="px-3 py-2 rounded-md shadow-sm min-w-[150px] max-w-[200px]"
      style={nodeStyles.section}
    >
      <Handle type="target" position={Position.Top} className="!bg-amber-400" />
      <p className="text-xs font-medium">{data.label}</p>
      {data.full_path && (
        <p className="text-xs opacity-70 mt-1 truncate">{data.full_path}</p>
      )}
    </div>
  );
}

// Node types mapping
const nodeTypes: NodeTypes = {
  answer: AnswerNode,
  claim: ClaimNode,
  source: SourceNode,
  section: SectionNode,
};

// Detail panel for selected node
function NodeDetailPanel({
  node,
  onClose,
}: {
  node: Node | null;
  onClose: () => void;
}) {
  if (!node) return null;

  const data = node.data as Record<string, any>;

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className="absolute right-4 top-4 w-80 bg-white rounded-xl shadow-xl border border-gray-200 overflow-hidden z-10"
    >
      <div className="p-4 border-b border-gray-100 flex items-center justify-between bg-gray-50">
        <h3 className="font-semibold text-gray-900 capitalize">{node.type} Details</h3>
        <button
          onClick={onClose}
          className="p-1 hover:bg-gray-200 rounded-lg transition-colors"
        >
          <X className="w-4 h-4 text-gray-500" />
        </button>
      </div>
      <div className="p-4 space-y-3 max-h-[400px] overflow-y-auto">
        {data.title && (
          <div>
            <label className="text-xs font-medium text-gray-500 uppercase">Title</label>
            <p className="text-sm text-gray-900">{data.title}</p>
          </div>
        )}
        {data.citation && (
          <div>
            <label className="text-xs font-medium text-gray-500 uppercase">Citation</label>
            <p className="text-sm text-gray-900 font-mono">{data.citation}</p>
          </div>
        )}
        {data.authority_level && (
          <div>
            <label className="text-xs font-medium text-gray-500 uppercase">Authority</label>
            <span
              className="inline-block mt-1 px-2 py-1 text-xs font-medium rounded-full"
              style={{
                backgroundColor: authorityColors[data.authority_level]?.bg || '#6b7280',
                color: authorityColors[data.authority_level]?.text || '#ffffff',
              }}
            >
              {typeof data.authority_level === 'number'
                ? ['', 'Federal', 'State', 'Regional', 'Utility'][data.authority_level]
                : data.authority_level}
            </span>
          </div>
        )}
        {(data.text || data.full_text || data.excerpt) && (
          <div>
            <label className="text-xs font-medium text-gray-500 uppercase">Content</label>
            <p className="text-sm text-gray-700 mt-1 whitespace-pre-wrap">
              {data.full_text || data.text || data.excerpt}
            </p>
          </div>
        )}
        {data.similarity_score && (
          <div>
            <label className="text-xs font-medium text-gray-500 uppercase">Similarity Score</label>
            <div className="flex items-center gap-2 mt-1">
              <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-green-500 rounded-full"
                  style={{ width: `${data.similarity_score * 100}%` }}
                />
              </div>
              <span className="text-sm font-medium">
                {Math.round(data.similarity_score * 100)}%
              </span>
            </div>
          </div>
        )}
        {data.url && (
          <a
            href={data.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 mt-2"
          >
            <ExternalLink className="w-4 h-4" />
            View Original Source
          </a>
        )}
      </div>
    </motion.div>
  );
}

export default function KnowledgeGraph({ graph, onClose }: KnowledgeGraphProps) {
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);

  // Convert API graph to React Flow format
  const initialNodes: Node[] = useMemo(
    () =>
      graph.nodes.map((node) => ({
        id: node.id,
        type: node.type,
        position: node.position,
        data: { ...node.data, label: node.data.label || node.id },
      })),
    [graph.nodes]
  );

  const initialEdges: Edge[] = useMemo(
    () =>
      graph.edges.map((edge) => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        type: edge.animated ? 'default' : 'smoothstep',
        animated: edge.animated,
        label: edge.label,
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: '#94a3b8',
        },
        style: { stroke: '#94a3b8', strokeWidth: 2 },
        labelStyle: { fontSize: 10, fill: '#64748b' },
        labelBgStyle: { fill: '#f8fafc', fillOpacity: 0.9 },
      })),
    [graph.edges]
  );

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
  }, []);

  const onPaneClick = useCallback(() => {
    setSelectedNode(null);
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
    >
      <motion.div
        initial={{ scale: 0.95 }}
        animate={{ scale: 1 }}
        exit={{ scale: 0.95 }}
        className="bg-white rounded-2xl shadow-2xl w-full max-w-6xl h-[80vh] overflow-hidden flex flex-col"
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-gray-50">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Source Lineage</h2>
            <p className="text-sm text-gray-500">
              Interactive visualization of how sources support the answer
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Legend */}
        <div className="px-6 py-2 border-b border-gray-100 flex items-center gap-6 text-xs">
          <span className="text-gray-500">Legend:</span>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-blue-600" />
            <span>Answer</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-slate-300" />
            <span>Claim</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-green-600" />
            <span>Source (State)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-blue-800" />
            <span>Source (Federal)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-amber-400" />
            <span>Section</span>
          </div>
        </div>

        {/* Graph */}
        <div className="flex-1 relative">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            onPaneClick={onPaneClick}
            nodeTypes={nodeTypes}
            fitView
            fitViewOptions={{ padding: 0.2 }}
            minZoom={0.3}
            maxZoom={1.5}
            defaultEdgeOptions={{
              type: 'smoothstep',
            }}
          >
            <Background color="#e2e8f0" gap={20} />
            <Controls className="!bg-white !shadow-lg !border !border-gray-200 !rounded-lg" />
            <MiniMap
              nodeColor={(node) => {
                switch (node.type) {
                  case 'answer':
                    return '#3b82f6';
                  case 'claim':
                    return '#94a3b8';
                  case 'source':
                    return '#10b981';
                  case 'section':
                    return '#f59e0b';
                  default:
                    return '#6b7280';
                }
              }}
              className="!bg-white !shadow-lg !border !border-gray-200 !rounded-lg"
            />
          </ReactFlow>

          {/* Detail Panel */}
          <AnimatePresence>
            {selectedNode && (
              <NodeDetailPanel
                node={selectedNode}
                onClose={() => setSelectedNode(null)}
              />
            )}
          </AnimatePresence>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-gray-200 bg-gray-50 text-xs text-gray-500">
          Click on a node to see details. Drag to pan, scroll to zoom.
        </div>
      </motion.div>
    </motion.div>
  );
}
