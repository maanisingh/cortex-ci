import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { riskJustificationApi, entitiesApi } from '../services/api'
import {
  ScaleIcon,
  DocumentTextIcon,
  ExclamationCircleIcon,
  CheckCircleIcon,
  ArrowPathIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline'

interface RiskFactor {
  factor: string
  contribution: number
  source: string
  evidence: string
  weight: number
}

interface RiskJustification {
  entity_id: string
  entity_name: string
  risk_score: number
  level: string
  justification: {
    primary_factors: RiskFactor[]
    assumptions: string[]
    uncertainty: {
      confidence: number
      factors: string[]
    }
    generated_at: string
    analyst_can_override: boolean
  }
  has_override: boolean
  override_info?: {
    original_score: number
    override_score: number
    override_reason: string
    overridden_by: string
    overridden_at: string
  }
}

interface Entity {
  id: string
  name: string
  type: string
  risk_score?: number
}

export default function RiskJustification() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedEntity, setSelectedEntity] = useState<string | null>(null)
  const [showOverrideModal, setShowOverrideModal] = useState(false)
  const [overrideData, setOverrideData] = useState({ new_score: 0, reason: '' })

  const queryClient = useQueryClient()

  const { data: entities, isLoading: entitiesLoading } = useQuery({
    queryKey: ['entities-for-justification', searchTerm],
    queryFn: async () => {
      const response = await entitiesApi.list({ search: searchTerm, page_size: 20 })
      return response.data.items || response.data
    },
    enabled: searchTerm.length > 2,
  })

  const { data: justification, isLoading: justificationLoading, error: justificationError } = useQuery({
    queryKey: ['risk-justification', selectedEntity],
    queryFn: async () => {
      const response = await riskJustificationApi.get(selectedEntity!)
      return response.data
    },
    enabled: !!selectedEntity,
  })

  const { data: history } = useQuery({
    queryKey: ['risk-justification-history', selectedEntity],
    queryFn: async () => {
      const response = await riskJustificationApi.history(selectedEntity!)
      return response.data
    },
    enabled: !!selectedEntity,
  })

  const overrideMutation = useMutation({
    mutationFn: (data: { new_score: number; reason: string }) =>
      riskJustificationApi.override(selectedEntity!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['risk-justification', selectedEntity] })
      setShowOverrideModal(false)
      setOverrideData({ new_score: 0, reason: '' })
    },
  })

  const riskLevelColors: Record<string, string> = {
    LOW: 'bg-green-100 text-green-800',
    MEDIUM: 'bg-yellow-100 text-yellow-800',
    HIGH: 'bg-orange-100 text-orange-800',
    CRITICAL: 'bg-red-100 text-red-800',
  }

  const confidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600'
    if (confidence >= 0.6) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Risk Justification Engine</h1>
        <p className="mt-2 text-sm text-gray-700">
          Legal defensibility and transparent risk scoring explanations
        </p>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Entity Search Panel */}
        <div className="card">
          <h2 className="font-semibold mb-4 flex items-center">
            <MagnifyingGlassIcon className="h-5 w-5 mr-2" />
            Search Entity
          </h2>
          <input
            type="text"
            placeholder="Search entities (min 3 chars)..."
            className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />

          <div className="mt-4 space-y-2 max-h-96 overflow-y-auto">
            {entitiesLoading ? (
              <div className="text-center text-gray-500 py-4">Searching...</div>
            ) : entities?.length === 0 ? (
              <div className="text-center text-gray-500 py-4">No entities found</div>
            ) : (
              entities?.map((entity: Entity) => (
                <button
                  key={entity.id}
                  onClick={() => setSelectedEntity(entity.id)}
                  className={`w-full text-left p-3 rounded-lg border transition-colors ${
                    selectedEntity === entity.id
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="font-medium">{entity.name}</div>
                  <div className="text-xs text-gray-500">{entity.type}</div>
                  {entity.risk_score !== undefined && (
                    <div className="text-sm mt-1">
                      Risk: <span className="font-semibold">{entity.risk_score.toFixed(1)}</span>
                    </div>
                  )}
                </button>
              ))
            )}
          </div>
        </div>

        {/* Justification Details */}
        <div className="col-span-2">
          {!selectedEntity ? (
            <div className="card text-center py-12">
              <ScaleIcon className="h-12 w-12 mx-auto text-gray-400" />
              <p className="mt-4 text-gray-500">Select an entity to view risk justification</p>
            </div>
          ) : justificationLoading ? (
            <div className="card text-center py-12">
              <ArrowPathIcon className="h-8 w-8 mx-auto text-gray-400 animate-spin" />
              <p className="mt-4 text-gray-500">Loading justification...</p>
            </div>
          ) : justificationError ? (
            <div className="card text-center py-12">
              <ExclamationCircleIcon className="h-12 w-12 mx-auto text-red-400" />
              <p className="mt-4 text-gray-500">No justification available for this entity</p>
            </div>
          ) : justification ? (
            <div className="space-y-4">
              {/* Header Card */}
              <div className="card">
                <div className="flex justify-between items-start">
                  <div>
                    <h2 className="text-xl font-bold">{justification.entity_name}</h2>
                    <div className="flex items-center gap-4 mt-2">
                      <div className="text-3xl font-bold">{justification.risk_score.toFixed(1)}</div>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${riskLevelColors[justification.level]}`}>
                        {justification.level}
                      </span>
                      {justification.has_override && (
                        <span className="px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800">
                          Override Applied
                        </span>
                      )}
                    </div>
                  </div>
                  {justification.justification.analyst_can_override && (
                    <button
                      onClick={() => {
                        setOverrideData({ new_score: justification.risk_score, reason: '' })
                        setShowOverrideModal(true)
                      }}
                      className="btn-secondary"
                    >
                      Override Score
                    </button>
                  )}
                </div>

                {justification.has_override && justification.override_info && (
                  <div className="mt-4 p-3 bg-purple-50 rounded-lg">
                    <div className="text-sm">
                      <span className="font-medium">Original Score:</span> {justification.override_info.original_score.toFixed(1)}
                      <span className="mx-2">-&gt;</span>
                      <span className="font-medium">Override:</span> {justification.override_info.override_score.toFixed(1)}
                    </div>
                    <div className="text-sm text-gray-600 mt-1">{justification.override_info.override_reason}</div>
                    <div className="text-xs text-gray-500 mt-1">
                      By {justification.override_info.overridden_by} on{' '}
                      {new Date(justification.override_info.overridden_at).toLocaleString()}
                    </div>
                  </div>
                )}
              </div>

              {/* Primary Factors */}
              <div className="card">
                <h3 className="font-semibold mb-4 flex items-center">
                  <DocumentTextIcon className="h-5 w-5 mr-2" />
                  Primary Risk Factors
                </h3>
                <div className="space-y-3">
                  {justification.justification.primary_factors.map((factor: RiskFactor, i: number) => (
                    <div key={i} className="border rounded-lg p-3">
                      <div className="flex justify-between items-start">
                        <div className="font-medium capitalize">{factor.factor.replace(/_/g, ' ')}</div>
                        <div className="text-lg font-bold text-primary-600">+{factor.contribution.toFixed(1)}</div>
                      </div>
                      <div className="text-sm text-gray-600 mt-1">{factor.evidence}</div>
                      <div className="flex justify-between items-center mt-2 text-xs text-gray-500">
                        <span>Source: {factor.source}</span>
                        <span>Weight: {(factor.weight * 100).toFixed(0)}%</span>
                      </div>
                      <div className="mt-2 h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary-500 rounded-full"
                          style={{ width: `${Math.min(100, factor.contribution)}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Uncertainty & Assumptions */}
              <div className="grid grid-cols-2 gap-4">
                <div className="card">
                  <h3 className="font-semibold mb-3">Confidence Level</h3>
                  <div className={`text-3xl font-bold ${confidenceColor(justification.justification.uncertainty.confidence)}`}>
                    {(justification.justification.uncertainty.confidence * 100).toFixed(0)}%
                  </div>
                  <div className="mt-3 space-y-1">
                    <div className="text-sm font-medium text-gray-700">Uncertainty Factors:</div>
                    {justification.justification.uncertainty.factors.map((f: string, i: number) => (
                      <div key={i} className="text-sm text-gray-600 flex items-start">
                        <ExclamationCircleIcon className="h-4 w-4 mr-1 text-yellow-500 flex-shrink-0 mt-0.5" />
                        {f}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="card">
                  <h3 className="font-semibold mb-3">Assumptions Made</h3>
                  <ul className="space-y-2">
                    {justification.justification.assumptions.map((assumption: string, i: number) => (
                      <li key={i} className="text-sm text-gray-600 flex items-start">
                        <CheckCircleIcon className="h-4 w-4 mr-1 text-green-500 flex-shrink-0 mt-0.5" />
                        {assumption}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* History */}
              {history && history.length > 0 && (
                <div className="card">
                  <h3 className="font-semibold mb-3">Justification History</h3>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {history.map((item: any, i: number) => (
                      <div key={i} className="text-sm border-b pb-2">
                        <div className="flex justify-between">
                          <span className="font-medium">Score: {item.risk_score.toFixed(1)}</span>
                          <span className="text-gray-500">{new Date(item.generated_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="text-xs text-gray-500 text-right">
                Generated: {new Date(justification.justification.generated_at).toLocaleString()}
              </div>
            </div>
          ) : null}
        </div>
      </div>

      {/* Override Modal */}
      {showOverrideModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Override Risk Score</h2>
            <form onSubmit={(e) => { e.preventDefault(); overrideMutation.mutate(overrideData); }}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">New Score (0-100)</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="0.1"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                    value={overrideData.new_score}
                    onChange={(e) => setOverrideData({ ...overrideData, new_score: parseFloat(e.target.value) })}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Justification Reason</label>
                  <textarea
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                    rows={4}
                    placeholder="Explain why you are overriding this score..."
                    value={overrideData.reason}
                    onChange={(e) => setOverrideData({ ...overrideData, reason: e.target.value })}
                    required
                  />
                </div>
              </div>
              <div className="mt-6 flex justify-end gap-3">
                <button type="button" className="btn-secondary" onClick={() => setShowOverrideModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary" disabled={overrideMutation.isPending}>
                  {overrideMutation.isPending ? 'Saving...' : 'Apply Override'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
