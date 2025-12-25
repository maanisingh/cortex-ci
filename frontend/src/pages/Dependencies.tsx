import { useState, useMemo, useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSearchParams, Link } from "react-router-dom";
import { PlusIcon } from "@heroicons/react/24/outline";
import DependencyForm from "../components/forms/DependencyForm";
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
} from "reactflow";
import "reactflow/dist/style.css";
import { dependenciesApi } from "../services/api";

interface GraphNode {
  id: string;
  label: string;
  type: string;
  criticality: number;
  risk_level: string | null;
  metadata: Record<string, any>;
}

interface GraphEdge {
  id: string;
  source: string;
  target: string;
  layer: string;
  relationship: string;
  criticality: number;
  is_bidirectional: boolean;
}

interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  stats: {
    total_nodes: number;
    total_edges: number;
    layers: Record<string, number>;
  };
}

const layerColors: Record<
  string,
  { bg: string; border: string; edge: string }
> = {
  legal: { bg: "#f3e8ff", border: "#a855f7", edge: "#a855f7" },
  financial: { bg: "#dbeafe", border: "#3b82f6", edge: "#3b82f6" },
  operational: { bg: "#dcfce7", border: "#22c55e", edge: "#22c55e" },
  academic: { bg: "#fef9c3", border: "#eab308", edge: "#eab308" },
  human: { bg: "#fee2e2", border: "#ef4444", edge: "#ef4444" },
};

const typeColors: Record<string, string> = {
  organization: "#3b82f6",
  individual: "#a855f7",
  location: "#22c55e",
  financial: "#eab308",
};

const riskColors: Record<string, string> = {
  critical: "#dc2626",
  high: "#f97316",
  medium: "#eab308",
  low: "#22c55e",
};

export default function Dependencies() {
  const [searchParams] = useSearchParams();
  const entityId = searchParams.get("entity_id");
  const [showForm, setShowForm] = useState(false);

  const { data: graphData, isLoading } = useQuery<GraphData>({
    queryKey: ["dependency-graph", entityId],
    queryFn: async () => {
      const response = await dependenciesApi.graph({
        entity_id: entityId || undefined,
        depth: 3,
      });
      return response.data;
    },
  });

  const { nodes: flowNodes, edges: flowEdges } = useMemo(() => {
    if (!graphData?.nodes || !graphData?.edges) {
      return { nodes: [], edges: [] };
    }

    // Calculate positions using a force-directed-like layout
    const nodeCount = graphData.nodes.length;
    const radius = Math.max(200, nodeCount * 30);
    const centerX = 400;
    const centerY = 300;

    const nodes: Node[] = graphData.nodes.map((node, index) => {
      // Arrange nodes in a circle
      const angle = (2 * Math.PI * index) / nodeCount;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);

      const nodeColor = typeColors[node.type?.toLowerCase()] || "#6b7280";
      const riskColor = node.risk_level
        ? riskColors[node.risk_level.toLowerCase()]
        : null;

      return {
        id: node.id,
        position: { x, y },
        data: {
          label: (
            <div className="text-center">
              <div
                className="font-medium text-sm truncate max-w-[120px]"
                title={node.label}
              >
                {node.label}
              </div>
              <div className="text-xs text-gray-500 capitalize">
                {node.type?.toLowerCase()}
              </div>
              {node.risk_level && (
                <div
                  className="text-xs mt-1 px-1 rounded"
                  style={{
                    backgroundColor: riskColor || "#e5e7eb",
                    color: "#fff",
                  }}
                >
                  {node.risk_level}
                </div>
              )}
            </div>
          ),
          type: node.type,
          criticality: node.criticality,
          risk_level: node.risk_level,
        },
        style: {
          background: "#fff",
          border: `2px solid ${riskColor || nodeColor}`,
          borderRadius: "8px",
          padding: "10px",
          minWidth: "140px",
          boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
        },
      };
    });

    const edges: Edge[] = graphData.edges.map((edge) => {
      const layerStyle =
        layerColors[edge.layer?.toLowerCase()] || layerColors.operational;
      return {
        id: edge.id,
        source: edge.source,
        target: edge.target,
        label: edge.relationship?.toLowerCase().replace(/_/g, " "),
        labelStyle: { fontSize: 10, fill: "#666" },
        labelBgStyle: { fill: "#fff", fillOpacity: 0.8 },
        style: {
          stroke: layerStyle.edge,
          strokeWidth: Math.max(1, edge.criticality / 2),
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: layerStyle.edge,
        },
        markerStart: edge.is_bidirectional
          ? {
              type: MarkerType.ArrowClosed,
              color: layerStyle.edge,
            }
          : undefined,
        animated: edge.criticality >= 4,
      };
    });

    return { nodes, edges };
  }, [graphData]);

  const [nodes, setNodes, onNodesChange] = useNodesState(flowNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(flowEdges);

  // Update nodes/edges when graphData changes
  useMemo(() => {
    setNodes(flowNodes);
    setEdges(flowEdges);
  }, [flowNodes, flowEdges, setNodes, setEdges]);

  const onNodeClick = useCallback((_: any, node: Node) => {
    // Navigate to entity detail
    window.location.href = `/entities/${node.id}`;
  }, []);

  const layerColorClasses: Record<string, string> = {
    legal: "bg-purple-100 text-purple-800",
    financial: "bg-blue-100 text-blue-800",
    operational: "bg-green-100 text-green-800",
    academic: "bg-yellow-100 text-yellow-800",
    human: "bg-red-100 text-red-800",
  };

  return (
    <div>
      <div className="sm:flex sm:items-center mb-6">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900">Dependency Graph</h1>
          <p className="mt-2 text-sm text-gray-700">
            Multi-layer dependency relationships between entities
            {entityId && (
              <span className="ml-2">
                •{" "}
                <Link
                  to="/dependencies"
                  className="text-primary-600 hover:underline"
                >
                  Clear filter
                </Link>
              </span>
            )}
          </p>
        </div>
        <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
          <button
            type="button"
            className="btn-primary"
            onClick={() => setShowForm(true)}
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Add Dependency
          </button>
        </div>
      </div>

      <DependencyForm
        isOpen={showForm}
        onClose={() => setShowForm(false)}
        preselectedSourceId={entityId || undefined}
      />

      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-3 mb-6">
        <div className="card">
          <dt className="text-sm font-medium text-gray-500">Total Nodes</dt>
          <dd className="mt-1 text-3xl font-semibold text-gray-900">
            {graphData?.stats?.total_nodes || 0}
          </dd>
        </div>
        <div className="card">
          <dt className="text-sm font-medium text-gray-500">Total Edges</dt>
          <dd className="mt-1 text-3xl font-semibold text-gray-900">
            {graphData?.stats?.total_edges || 0}
          </dd>
        </div>
        <div className="card">
          <dt className="text-sm font-medium text-gray-500">Layers</dt>
          <dd className="mt-1 flex flex-wrap gap-2">
            {Object.entries(graphData?.stats?.layers || {}).map(
              ([layer, count]) => (
                <span
                  key={layer}
                  className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${
                    layerColorClasses[layer.toLowerCase()] ||
                    "bg-gray-100 text-gray-800"
                  }`}
                >
                  {layer}: {count as number}
                </span>
              ),
            )}
          </dd>
        </div>
      </div>

      {/* Legend */}
      <div className="card mb-4">
        <div className="flex flex-wrap gap-6 text-sm">
          <div>
            <span className="font-medium text-gray-700">Entity Types:</span>
            <div className="flex gap-3 mt-1">
              {Object.entries(typeColors).map(([type, color]) => (
                <span key={type} className="flex items-center gap-1">
                  <span
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: color }}
                  />
                  <span className="capitalize">{type}</span>
                </span>
              ))}
            </div>
          </div>
          <div>
            <span className="font-medium text-gray-700">Risk Levels:</span>
            <div className="flex gap-3 mt-1">
              {Object.entries(riskColors).map(([level, color]) => (
                <span key={level} className="flex items-center gap-1">
                  <span
                    className="w-3 h-3 rounded"
                    style={{ backgroundColor: color }}
                  />
                  <span className="capitalize">{level}</span>
                </span>
              ))}
            </div>
          </div>
          <div>
            <span className="font-medium text-gray-700">
              Dependency Layers:
            </span>
            <div className="flex gap-3 mt-1">
              {Object.entries(layerColors).map(([layer, colors]) => (
                <span key={layer} className="flex items-center gap-1">
                  <span
                    className="w-4 h-0.5"
                    style={{ backgroundColor: colors.edge }}
                  />
                  <span className="capitalize">{layer}</span>
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Graph */}
      <div className="card" style={{ height: "600px" }}>
        {isLoading ? (
          <div className="h-full flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : nodes.length > 0 ? (
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            fitView
            attributionPosition="bottom-left"
          >
            <Background color="#f0f0f0" gap={16} />
            <Controls />
            <MiniMap
              nodeColor={(node) => {
                const type = (node.data as any)?.type?.toLowerCase();
                return typeColors[type] || "#6b7280";
              }}
              maskColor="rgba(0, 0, 0, 0.1)"
            />
          </ReactFlow>
        ) : (
          <div className="h-full flex items-center justify-center bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
            <div className="text-center">
              <p className="text-gray-500">No dependencies found</p>
              <p className="text-sm text-gray-400">
                Add entities and create dependencies to see the graph
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Tips */}
      <div className="mt-4 text-sm text-gray-500">
        <p>
          <strong>Tips:</strong> Click and drag to pan. Scroll to zoom. Click on
          a node to view entity details. High-criticality dependencies are
          animated.
        </p>
      </div>
    </div>
  );
}
