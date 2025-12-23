import { useQuery } from '@tanstack/react-query'
import { dependenciesApi } from '../services/api'

export default function Dependencies() {
  const { data: graphData, isLoading } = useQuery({
    queryKey: ['dependency-graph'],
    queryFn: async () => {
      const response = await dependenciesApi.graph()
      return response.data
    },
  })

  const layerColors: Record<string, string> = {
    legal: 'bg-purple-100 text-purple-800',
    financial: 'bg-blue-100 text-blue-800',
    operational: 'bg-green-100 text-green-800',
    academic: 'bg-yellow-100 text-yellow-800',
    human: 'bg-red-100 text-red-800',
  }

  return (
    <div>
      <div className="sm:flex sm:items-center mb-6">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900">Dependency Graph</h1>
          <p className="mt-2 text-sm text-gray-700">
            Multi-layer dependency relationships between entities
          </p>
        </div>
      </div>

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
            {Object.entries(graphData?.stats?.layers || {}).map(([layer, count]) => (
              <span
                key={layer}
                className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  layerColors[layer] || 'bg-gray-100 text-gray-800'
                }`}
              >
                {layer}: {count as number}
              </span>
            ))}
          </dd>
        </div>
      </div>

      {/* Graph Placeholder */}
      <div className="card">
        <div className="h-96 flex items-center justify-center bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          {isLoading ? (
            <span className="text-gray-500">Loading graph...</span>
          ) : graphData?.nodes?.length > 0 ? (
            <div className="text-center">
              <p className="text-gray-500 mb-2">
                Graph visualization with {graphData.nodes.length} nodes and{' '}
                {graphData.edges.length} edges
              </p>
              <p className="text-sm text-gray-400">
                (React Flow / D3.js visualization would render here)
              </p>
            </div>
          ) : (
            <div className="text-center">
              <p className="text-gray-500">No dependencies found</p>
              <p className="text-sm text-gray-400">Add entities and create dependencies to see the graph</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
