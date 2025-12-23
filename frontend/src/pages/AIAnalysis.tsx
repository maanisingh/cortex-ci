import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { aiApi } from '../services/api'
import {
  SparklesIcon,
  PlusIcon,
  CheckIcon,
  XMarkIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  BeakerIcon,
  CpuChipIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline'

interface AIAnalysis {
  id: string
  analysis_type: 'anomaly' | 'pattern' | 'summary' | 'scenario' | 'clustering'
  description: string
  status: 'pending' | 'processing' | 'completed' | 'approved' | 'rejected'
  input_data: Record<string, any>
  output?: Record<string, any>
  confidence?: number
  model_version: string
  requires_human_approval: boolean
  approved_by?: string
  approved_at?: string
  rejection_reason?: string
  created_at: string
  completed_at?: string
}

interface Anomaly {
  id: string
  entity_id: string
  entity_name: string
  anomaly_type: string
  description: string
  confidence: number
  is_confirmed?: boolean
  reviewed_at?: string
  reviewed_by?: string
  review_notes?: string
}

export default function AIAnalysis() {
  const [activeTab, setActiveTab] = useState<'analyses' | 'anomalies' | 'models'>('analyses')
  const [showRequestModal, setShowRequestModal] = useState(false)
  const [selectedAnalysis, setSelectedAnalysis] = useState<AIAnalysis | null>(null)
  const [requestForm, setRequestForm] = useState({
    analysis_type: 'anomaly' as const,
    description: '',
    entity_ids: [] as string[],
    parameters: {} as Record<string, any>
  })

  const queryClient = useQueryClient()

  const { data: analyses, isLoading: analysesLoading } = useQuery({
    queryKey: ['ai-analyses'],
    queryFn: async () => {
      const response = await aiApi.list()
      return response.data.items || response.data
    },
    enabled: activeTab === 'analyses',
  })

  const { data: anomalies, isLoading: anomaliesLoading } = useQuery({
    queryKey: ['ai-anomalies'],
    queryFn: async () => {
      const response = await aiApi.anomalies.pending()
      return response.data.items || response.data
    },
    enabled: activeTab === 'anomalies',
  })

  const requestMutation = useMutation({
    mutationFn: (data: typeof requestForm) => aiApi.request(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai-analyses'] })
      setShowRequestModal(false)
      setRequestForm({ analysis_type: 'anomaly', description: '', entity_ids: [], parameters: {} })
    },
  })

  const approveMutation = useMutation({
    mutationFn: (id: string) => aiApi.approve(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai-analyses'] })
      setSelectedAnalysis(null)
    },
  })

  const rejectMutation = useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) => aiApi.reject(id, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai-analyses'] })
      setSelectedAnalysis(null)
    },
  })

  const reviewAnomalyMutation = useMutation({
    mutationFn: ({ id, isConfirmed, notes }: { id: string; isConfirmed: boolean; notes?: string }) =>
      aiApi.anomalies.review(id, { is_confirmed: isConfirmed, notes }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai-anomalies'] })
    },
  })

  const analysisTypes = [
    { value: 'anomaly', label: 'Anomaly Detection', icon: ExclamationTriangleIcon, description: 'Detect unusual patterns in entity risk scores' },
    { value: 'pattern', label: 'Pattern Recognition', icon: ChartBarIcon, description: 'Identify recurring patterns in data' },
    { value: 'summary', label: 'Report Summary', icon: SparklesIcon, description: 'Generate natural language summaries' },
    { value: 'scenario', label: 'Scenario Acceleration', icon: BeakerIcon, description: 'Accelerate stress test simulations' },
    { value: 'clustering', label: 'Entity Clustering', icon: CpuChipIcon, description: 'Group similar entities together' },
  ]

  const statusColors: Record<string, string> = {
    pending: 'bg-gray-100 text-gray-800',
    processing: 'bg-blue-100 text-blue-800',
    completed: 'bg-yellow-100 text-yellow-800',
    approved: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
  }

  const confidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600'
    if (confidence >= 0.6) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <div>
      <div className="sm:flex sm:items-center mb-6">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900">AI Analysis</h1>
          <p className="mt-2 text-sm text-gray-700">
            Controlled AI with human-in-the-loop approval for pattern detection and analysis
          </p>
        </div>
        <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
          <button type="button" className="btn-primary" onClick={() => setShowRequestModal(true)}>
            <PlusIcon className="h-5 w-5 mr-2" />
            Request Analysis
          </button>
        </div>
      </div>

      {/* AI Boundaries Notice */}
      <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex">
          <SparklesIcon className="h-5 w-5 text-blue-500 mr-2 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-blue-800">
            <span className="font-semibold">Controlled AI:</span> All AI outputs require human approval before action.
            AI is limited to pattern detection, anomaly flagging, and report summarization.
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('analyses')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'analyses'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <CpuChipIcon className="h-5 w-5 inline mr-2" />
            Analysis Requests
          </button>
          <button
            onClick={() => setActiveTab('anomalies')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'anomalies'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <ExclamationTriangleIcon className="h-5 w-5 inline mr-2" />
            Pending Anomalies
          </button>
          <button
            onClick={() => setActiveTab('models')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'models'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <BeakerIcon className="h-5 w-5 inline mr-2" />
            Model Cards
          </button>
        </nav>
      </div>

      {/* Analyses Tab */}
      {activeTab === 'analyses' && (
        <div className="space-y-4">
          {analysesLoading ? (
            <div className="card text-center py-8 text-gray-500">Loading analyses...</div>
          ) : !analyses?.length ? (
            <div className="card text-center py-8 text-gray-500">
              No AI analyses requested yet. Click "Request Analysis" to start.
            </div>
          ) : (
            analyses.map((analysis: AIAnalysis) => (
              <div key={analysis.id} className="card">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${statusColors[analysis.status]}`}>
                        {analysis.status}
                      </span>
                      <span className="px-2 py-1 rounded text-xs font-medium bg-purple-100 text-purple-800">
                        {analysisTypes.find(t => t.value === analysis.analysis_type)?.label || analysis.analysis_type}
                      </span>
                      {analysis.requires_human_approval && (
                        <span className="px-2 py-1 rounded text-xs font-medium bg-orange-100 text-orange-800">
                          Requires Approval
                        </span>
                      )}
                    </div>
                    <p className="font-medium mt-2">{analysis.description}</p>
                    <div className="text-sm text-gray-500 mt-1 flex items-center gap-4">
                      <span className="flex items-center">
                        <ClockIcon className="h-4 w-4 mr-1" />
                        {new Date(analysis.created_at).toLocaleString()}
                      </span>
                      {analysis.confidence !== undefined && (
                        <span className={`font-medium ${confidenceColor(analysis.confidence)}`}>
                          Confidence: {(analysis.confidence * 100).toFixed(0)}%
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    {analysis.status === 'completed' && analysis.requires_human_approval && (
                      <>
                        <button
                          onClick={() => approveMutation.mutate(analysis.id)}
                          className="btn-primary text-sm"
                          disabled={approveMutation.isPending}
                        >
                          <CheckIcon className="h-4 w-4 mr-1" />
                          Approve
                        </button>
                        <button
                          onClick={() => {
                            const reason = prompt('Enter rejection reason:')
                            if (reason) rejectMutation.mutate({ id: analysis.id, reason })
                          }}
                          className="btn-secondary text-sm"
                          disabled={rejectMutation.isPending}
                        >
                          <XMarkIcon className="h-4 w-4 mr-1" />
                          Reject
                        </button>
                      </>
                    )}
                    <button
                      onClick={() => setSelectedAnalysis(analysis)}
                      className="text-primary-600 hover:text-primary-800 text-sm"
                    >
                      View Details
                    </button>
                  </div>
                </div>

                {analysis.status === 'rejected' && analysis.rejection_reason && (
                  <div className="mt-3 p-3 bg-red-50 rounded-lg text-sm text-red-800">
                    <span className="font-medium">Rejection Reason:</span> {analysis.rejection_reason}
                  </div>
                )}

                {analysis.output && analysis.status !== 'pending' && analysis.status !== 'processing' && (
                  <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                    <div className="text-sm font-medium text-gray-700 mb-2">Output Preview:</div>
                    <pre className="text-xs text-gray-600 overflow-x-auto max-h-32">
                      {JSON.stringify(analysis.output, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* Anomalies Tab */}
      {activeTab === 'anomalies' && (
        <div className="space-y-4">
          {anomaliesLoading ? (
            <div className="card text-center py-8 text-gray-500">Loading anomalies...</div>
          ) : !anomalies?.length ? (
            <div className="card text-center py-8 text-gray-500">
              No pending anomalies to review.
            </div>
          ) : (
            anomalies.map((anomaly: Anomaly) => (
              <div key={anomaly.id} className="card">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <ExclamationTriangleIcon className="h-5 w-5 text-orange-500" />
                      <span className="font-medium">{anomaly.entity_name}</span>
                      <span className="px-2 py-1 rounded text-xs font-medium bg-orange-100 text-orange-800">
                        {anomaly.anomaly_type}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mt-2">{anomaly.description}</p>
                    <div className={`text-sm mt-2 font-medium ${confidenceColor(anomaly.confidence)}`}>
                      Confidence: {(anomaly.confidence * 100).toFixed(0)}%
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => reviewAnomalyMutation.mutate({ id: anomaly.id, isConfirmed: true })}
                      className="btn-primary text-sm"
                      disabled={reviewAnomalyMutation.isPending}
                    >
                      <CheckIcon className="h-4 w-4 mr-1" />
                      Confirm
                    </button>
                    <button
                      onClick={() => reviewAnomalyMutation.mutate({ id: anomaly.id, isConfirmed: false, notes: 'False positive' })}
                      className="btn-secondary text-sm"
                      disabled={reviewAnomalyMutation.isPending}
                    >
                      <XMarkIcon className="h-4 w-4 mr-1" />
                      Dismiss
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Model Cards Tab */}
      {activeTab === 'models' && (
        <div className="grid grid-cols-2 gap-4">
          {analysisTypes.map((type) => (
            <div key={type.value} className="card">
              <div className="flex items-start">
                <type.icon className="h-8 w-8 text-primary-500 mr-3" />
                <div>
                  <h3 className="font-semibold">{type.label}</h3>
                  <p className="text-sm text-gray-600 mt-1">{type.description}</p>
                  <div className="mt-3 text-xs text-gray-500">
                    <div><span className="font-medium">Model:</span> Isolation Forest / K-Means</div>
                    <div><span className="font-medium">Requires Approval:</span> Yes</div>
                    <div><span className="font-medium">Explainability:</span> Factor-based</div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Request Modal */}
      {showRequestModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-lg">
            <h2 className="text-xl font-bold mb-4">Request AI Analysis</h2>
            <form onSubmit={(e) => { e.preventDefault(); requestMutation.mutate(requestForm); }}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Analysis Type</label>
                  <select
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                    value={requestForm.analysis_type}
                    onChange={(e) => setRequestForm({ ...requestForm, analysis_type: e.target.value as any })}
                  >
                    {analysisTypes.map(type => (
                      <option key={type.value} value={type.value}>{type.label}</option>
                    ))}
                  </select>
                  <p className="text-xs text-gray-500 mt-1">
                    {analysisTypes.find(t => t.value === requestForm.analysis_type)?.description}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Description</label>
                  <textarea
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                    rows={3}
                    placeholder="Describe what you want to analyze..."
                    value={requestForm.description}
                    onChange={(e) => setRequestForm({ ...requestForm, description: e.target.value })}
                    required
                  />
                </div>
              </div>
              <div className="mt-6 flex justify-end gap-3">
                <button type="button" className="btn-secondary" onClick={() => setShowRequestModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary" disabled={requestMutation.isPending}>
                  {requestMutation.isPending ? 'Submitting...' : 'Submit Request'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Analysis Detail Modal */}
      {selectedAnalysis && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto">
          <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-3xl my-8 mx-4">
            <div className="flex justify-between items-start mb-4">
              <h2 className="text-xl font-bold">Analysis Details</h2>
              <button onClick={() => setSelectedAnalysis(null)} className="text-gray-400 hover:text-gray-600">
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-gray-500">Type</div>
                  <div className="font-medium">
                    {analysisTypes.find(t => t.value === selectedAnalysis.analysis_type)?.label}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">Status</div>
                  <span className={`px-2 py-1 rounded text-sm font-medium ${statusColors[selectedAnalysis.status]}`}>
                    {selectedAnalysis.status}
                  </span>
                </div>
                <div>
                  <div className="text-sm text-gray-500">Created</div>
                  <div className="font-medium">{new Date(selectedAnalysis.created_at).toLocaleString()}</div>
                </div>
                {selectedAnalysis.confidence !== undefined && (
                  <div>
                    <div className="text-sm text-gray-500">Confidence</div>
                    <div className={`font-medium ${confidenceColor(selectedAnalysis.confidence)}`}>
                      {(selectedAnalysis.confidence * 100).toFixed(0)}%
                    </div>
                  </div>
                )}
              </div>

              <div>
                <div className="text-sm text-gray-500 mb-1">Description</div>
                <div className="p-3 bg-gray-50 rounded-lg">{selectedAnalysis.description}</div>
              </div>

              <div>
                <div className="text-sm text-gray-500 mb-1">Input Data</div>
                <pre className="p-3 bg-gray-50 rounded-lg text-xs overflow-x-auto max-h-40">
                  {JSON.stringify(selectedAnalysis.input_data, null, 2)}
                </pre>
              </div>

              {selectedAnalysis.output && (
                <div>
                  <div className="text-sm text-gray-500 mb-1">Output</div>
                  <pre className="p-3 bg-gray-50 rounded-lg text-xs overflow-x-auto max-h-60">
                    {JSON.stringify(selectedAnalysis.output, null, 2)}
                  </pre>
                </div>
              )}

              <div className="text-xs text-gray-500">
                Model Version: {selectedAnalysis.model_version}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
