import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { historyApi, entitiesApi } from '../services/api'
import {
  ClockIcon,
  DocumentCheckIcon,
  PlusIcon,
  CheckCircleIcon,
  XCircleIcon,
  CalendarIcon,
  BookOpenIcon
} from '@heroicons/react/24/outline'

interface Decision {
  id: string
  decision_date: string
  decision_summary: string
  decision_type: string
  entities_involved: string[]
  outcome_date?: string
  outcome_summary?: string
  outcome_success?: boolean
  lessons_learned?: string
  is_resolved: boolean
  created_at: string
}

interface TimelineEvent {
  date: string
  type: string
  description: string
  risk_score_before?: number
  risk_score_after?: number
}

export default function History() {
  const [activeTab, setActiveTab] = useState<'decisions' | 'timeline' | 'constraints'>('decisions')
  const [showDecisionModal, setShowDecisionModal] = useState(false)
  const [showOutcomeModal, setShowOutcomeModal] = useState(false)
  const [selectedDecision, setSelectedDecision] = useState<Decision | null>(null)
  const [selectedEntityId, setSelectedEntityId] = useState<string>('')
  const [searchTerm, setSearchTerm] = useState('')
  const [decisionForm, setDecisionForm] = useState({
    decision_date: new Date().toISOString().split('T')[0],
    decision_summary: '',
    decision_type: 'risk_acceptance',
    entities_involved: [] as string[]
  })
  const [outcomeForm, setOutcomeForm] = useState({
    outcome_summary: '',
    outcome_success: true,
    lessons_learned: ''
  })

  const queryClient = useQueryClient()

  const { data: decisions, isLoading: decisionsLoading } = useQuery({
    queryKey: ['decisions'],
    queryFn: async () => {
      const response = await historyApi.decisions.list({ include_resolved: true })
      return response.data.items || response.data
    },
    enabled: activeTab === 'decisions',
  })

  const { data: entities } = useQuery({
    queryKey: ['entities-search', searchTerm],
    queryFn: async () => {
      const response = await entitiesApi.list({ search: searchTerm, page_size: 10 })
      return response.data.items || response.data
    },
    enabled: searchTerm.length > 2,
  })

  const { data: timeline, isLoading: timelineLoading } = useQuery({
    queryKey: ['entity-timeline', selectedEntityId],
    queryFn: async () => {
      const response = await historyApi.entityTimeline(selectedEntityId, 365)
      return response.data
    },
    enabled: activeTab === 'timeline' && !!selectedEntityId,
  })

  const { data: constraintChanges, isLoading: constraintsLoading } = useQuery({
    queryKey: ['constraint-changes'],
    queryFn: async () => {
      const response = await historyApi.constraintChanges(90)
      return response.data
    },
    enabled: activeTab === 'constraints',
  })

  const createDecisionMutation = useMutation({
    mutationFn: (data: typeof decisionForm) => historyApi.decisions.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['decisions'] })
      setShowDecisionModal(false)
      setDecisionForm({
        decision_date: new Date().toISOString().split('T')[0],
        decision_summary: '',
        decision_type: 'risk_acceptance',
        entities_involved: []
      })
    },
  })

  const recordOutcomeMutation = useMutation({
    mutationFn: (data: typeof outcomeForm) =>
      historyApi.decisions.recordOutcome(selectedDecision!.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['decisions'] })
      setShowOutcomeModal(false)
      setSelectedDecision(null)
      setOutcomeForm({ outcome_summary: '', outcome_success: true, lessons_learned: '' })
    },
  })

  const decisionTypes = [
    { value: 'risk_acceptance', label: 'Risk Acceptance' },
    { value: 'mitigation', label: 'Mitigation Action' },
    { value: 'escalation', label: 'Escalation' },
    { value: 'policy_change', label: 'Policy Change' },
    { value: 'exception', label: 'Exception Granted' },
  ]

  return (
    <div>
      <div className="sm:flex sm:items-center mb-6">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900">Institutional Memory</h1>
          <p className="mt-2 text-sm text-gray-700">
            Decision tracking, timeline views, and organizational knowledge preservation
          </p>
        </div>
        {activeTab === 'decisions' && (
          <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
            <button type="button" className="btn-primary" onClick={() => setShowDecisionModal(true)}>
              <PlusIcon className="h-5 w-5 mr-2" />
              Record Decision
            </button>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('decisions')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'decisions'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <DocumentCheckIcon className="h-5 w-5 inline mr-2" />
            Decisions & Outcomes
          </button>
          <button
            onClick={() => setActiveTab('timeline')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'timeline'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <ClockIcon className="h-5 w-5 inline mr-2" />
            Entity Timeline
          </button>
          <button
            onClick={() => setActiveTab('constraints')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'constraints'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <BookOpenIcon className="h-5 w-5 inline mr-2" />
            Constraint Changes
          </button>
        </nav>
      </div>

      {/* Decisions Tab */}
      {activeTab === 'decisions' && (
        <div className="space-y-4">
          {decisionsLoading ? (
            <div className="card text-center py-8 text-gray-500">Loading decisions...</div>
          ) : !decisions?.length ? (
            <div className="card text-center py-8 text-gray-500">
              No decisions recorded yet. Click "Record Decision" to add one.
            </div>
          ) : (
            decisions.map((decision: Decision) => (
              <div key={decision.id} className="card">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        decision.is_resolved
                          ? 'bg-green-100 text-green-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {decision.is_resolved ? 'Resolved' : 'Pending Outcome'}
                      </span>
                      <span className="px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-800">
                        {decisionTypes.find(t => t.value === decision.decision_type)?.label || decision.decision_type}
                      </span>
                    </div>
                    <h3 className="font-semibold mt-2">{decision.decision_summary}</h3>
                    <div className="text-sm text-gray-500 mt-1 flex items-center">
                      <CalendarIcon className="h-4 w-4 mr-1" />
                      Decision Date: {new Date(decision.decision_date).toLocaleDateString()}
                    </div>
                    {decision.entities_involved?.length > 0 && (
                      <div className="text-sm text-gray-500 mt-1">
                        Entities: {decision.entities_involved.length} involved
                      </div>
                    )}
                  </div>
                  {!decision.is_resolved && (
                    <button
                      onClick={() => {
                        setSelectedDecision(decision)
                        setShowOutcomeModal(true)
                      }}
                      className="btn-secondary text-sm"
                    >
                      Record Outcome
                    </button>
                  )}
                </div>

                {decision.is_resolved && (
                  <div className="mt-4 pt-4 border-t">
                    <div className="flex items-center gap-2 mb-2">
                      {decision.outcome_success ? (
                        <CheckCircleIcon className="h-5 w-5 text-green-500" />
                      ) : (
                        <XCircleIcon className="h-5 w-5 text-red-500" />
                      )}
                      <span className="font-medium">
                        Outcome: {decision.outcome_success ? 'Successful' : 'Unsuccessful'}
                      </span>
                      <span className="text-sm text-gray-500">
                        ({new Date(decision.outcome_date!).toLocaleDateString()})
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">{decision.outcome_summary}</p>
                    {decision.lessons_learned && (
                      <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                        <div className="text-sm font-medium text-blue-900">Lessons Learned:</div>
                        <p className="text-sm text-blue-800 mt-1">{decision.lessons_learned}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* Timeline Tab */}
      {activeTab === 'timeline' && (
        <div className="grid grid-cols-3 gap-6">
          <div className="card">
            <h3 className="font-semibold mb-3">Select Entity</h3>
            <input
              type="text"
              placeholder="Search entities..."
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 mb-3"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {entities?.map((entity: any) => (
                <button
                  key={entity.id}
                  onClick={() => setSelectedEntityId(entity.id)}
                  className={`w-full text-left p-2 rounded border ${
                    selectedEntityId === entity.id
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="font-medium text-sm">{entity.name}</div>
                  <div className="text-xs text-gray-500">{entity.type}</div>
                </button>
              ))}
            </div>
          </div>

          <div className="col-span-2 card">
            <h3 className="font-semibold mb-4">Timeline (Last 365 Days)</h3>
            {!selectedEntityId ? (
              <div className="text-center py-8 text-gray-500">
                Select an entity to view its timeline
              </div>
            ) : timelineLoading ? (
              <div className="text-center py-8 text-gray-500">Loading timeline...</div>
            ) : !timeline?.length ? (
              <div className="text-center py-8 text-gray-500">No timeline events found</div>
            ) : (
              <div className="relative">
                <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200" />
                <div className="space-y-4">
                  {timeline.map((event: TimelineEvent, i: number) => (
                    <div key={i} className="relative pl-10">
                      <div className="absolute left-2.5 w-3 h-3 rounded-full bg-primary-500" />
                      <div className="bg-gray-50 p-3 rounded-lg">
                        <div className="flex justify-between items-start">
                          <div className="text-sm font-medium">{event.type}</div>
                          <div className="text-xs text-gray-500">
                            {new Date(event.date).toLocaleDateString()}
                          </div>
                        </div>
                        <p className="text-sm text-gray-600 mt-1">{event.description}</p>
                        {event.risk_score_before !== undefined && (
                          <div className="text-xs mt-2">
                            Risk: {event.risk_score_before?.toFixed(1)} -&gt; {event.risk_score_after?.toFixed(1)}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Constraint Changes Tab */}
      {activeTab === 'constraints' && (
        <div className="card">
          <h3 className="font-semibold mb-4">Recent Constraint Changes (Last 90 Days)</h3>
          {constraintsLoading ? (
            <div className="text-center py-8 text-gray-500">Loading changes...</div>
          ) : !constraintChanges?.length ? (
            <div className="text-center py-8 text-gray-500">No constraint changes in the last 90 days</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="table-header">Date</th>
                    <th className="table-header">Constraint</th>
                    <th className="table-header">Change Type</th>
                    <th className="table-header">Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {constraintChanges.map((change: any, i: number) => (
                    <tr key={i} className="hover:bg-gray-50">
                      <td className="table-cell">{new Date(change.changed_at).toLocaleDateString()}</td>
                      <td className="table-cell font-medium">{change.constraint_name}</td>
                      <td className="table-cell">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          change.change_type === 'created' ? 'bg-green-100 text-green-800' :
                          change.change_type === 'updated' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {change.change_type}
                        </span>
                      </td>
                      <td className="table-cell text-sm text-gray-600">{change.change_summary}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Decision Modal */}
      {showDecisionModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-lg">
            <h2 className="text-xl font-bold mb-4">Record Decision</h2>
            <form onSubmit={(e) => { e.preventDefault(); createDecisionMutation.mutate(decisionForm); }}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Decision Date</label>
                  <input
                    type="date"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                    value={decisionForm.decision_date}
                    onChange={(e) => setDecisionForm({ ...decisionForm, decision_date: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Decision Type</label>
                  <select
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                    value={decisionForm.decision_type}
                    onChange={(e) => setDecisionForm({ ...decisionForm, decision_type: e.target.value })}
                  >
                    {decisionTypes.map(type => (
                      <option key={type.value} value={type.value}>{type.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Decision Summary</label>
                  <textarea
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                    rows={3}
                    value={decisionForm.decision_summary}
                    onChange={(e) => setDecisionForm({ ...decisionForm, decision_summary: e.target.value })}
                    required
                  />
                </div>
              </div>
              <div className="mt-6 flex justify-end gap-3">
                <button type="button" className="btn-secondary" onClick={() => setShowDecisionModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary" disabled={createDecisionMutation.isPending}>
                  {createDecisionMutation.isPending ? 'Saving...' : 'Record Decision'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Outcome Modal */}
      {showOutcomeModal && selectedDecision && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-lg">
            <h2 className="text-xl font-bold mb-4">Record Outcome</h2>
            <div className="mb-4 p-3 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-500">Decision:</div>
              <div className="font-medium">{selectedDecision.decision_summary}</div>
            </div>
            <form onSubmit={(e) => { e.preventDefault(); recordOutcomeMutation.mutate(outcomeForm); }}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Was the outcome successful?</label>
                  <div className="mt-2 flex gap-4">
                    <label className="flex items-center">
                      <input
                        type="radio"
                        checked={outcomeForm.outcome_success}
                        onChange={() => setOutcomeForm({ ...outcomeForm, outcome_success: true })}
                        className="mr-2"
                      />
                      Yes
                    </label>
                    <label className="flex items-center">
                      <input
                        type="radio"
                        checked={!outcomeForm.outcome_success}
                        onChange={() => setOutcomeForm({ ...outcomeForm, outcome_success: false })}
                        className="mr-2"
                      />
                      No
                    </label>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Outcome Summary</label>
                  <textarea
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                    rows={3}
                    value={outcomeForm.outcome_summary}
                    onChange={(e) => setOutcomeForm({ ...outcomeForm, outcome_summary: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Lessons Learned (Optional)</label>
                  <textarea
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                    rows={3}
                    placeholder="What did we learn from this decision?"
                    value={outcomeForm.lessons_learned}
                    onChange={(e) => setOutcomeForm({ ...outcomeForm, lessons_learned: e.target.value })}
                  />
                </div>
              </div>
              <div className="mt-6 flex justify-end gap-3">
                <button type="button" className="btn-secondary" onClick={() => setShowOutcomeModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary" disabled={recordOutcomeMutation.isPending}>
                  {recordOutcomeMutation.isPending ? 'Saving...' : 'Record Outcome'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
