import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { entitiesApi, dependenciesApi, risksApi } from '../services/api'

interface Entity {
  id: string
  name: string
  type: string
  aliases: string[]
  country_code: string
  category: string
  subcategory: string
  criticality: number
  tags: string[]
  is_active: boolean
  notes: string
  custom_data: Record<string, any>
  created_at: string
  updated_at: string
}

interface RiskScore {
  overall_score: number
  risk_level: string
  constraint_score: number
  dependency_score: number
  country_score: number
}

interface Dependency {
  id: string
  source_entity_id: string
  target_entity_id: string
  source_entity_name: string
  target_entity_name: string
  layer: string
  relationship_type: string
  criticality: number
}

export default function EntityDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [entity, setEntity] = useState<Entity | null>(null)
  const [riskScore, setRiskScore] = useState<RiskScore | null>(null)
  const [dependencies, setDependencies] = useState<Dependency[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (id) {
      loadEntityData()
    }
  }, [id])

  const loadEntityData = async () => {
    try {
      setLoading(true)
      const [entityRes, depsRes] = await Promise.all([
        entitiesApi.get(id!),
        dependenciesApi.list({ entity_id: id }),
      ])
      setEntity(entityRes.data)
      setDependencies(depsRes.data.items || [])

      // Try to get risk score
      try {
        const riskRes = await risksApi.entityRisk(id!)
        setRiskScore(riskRes.data)
      } catch {
        // Risk score might not exist yet
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load entity')
    } finally {
      setLoading(false)
    }
  }

  const getRiskColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200'
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200'
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'low': return 'bg-green-100 text-green-800 border-green-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getCriticalityLabel = (c: number) => {
    const labels = ['', 'Very Low', 'Low', 'Medium', 'High', 'Critical']
    return labels[c] || 'Unknown'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (error || !entity) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700">{error || 'Entity not found'}</p>
        <button onClick={() => navigate('/entities')} className="mt-2 text-red-600 underline">
          Back to Entities
        </button>
      </div>
    )
  }

  const incomingDeps = dependencies.filter(d => d.target_entity_id === id)
  const outgoingDeps = dependencies.filter(d => d.source_entity_id === id)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <button
            onClick={() => navigate('/entities')}
            className="text-sm text-gray-500 hover:text-gray-700 mb-2 flex items-center"
          >
            ← Back to Entities
          </button>
          <h1 className="text-2xl font-bold text-gray-900">{entity.name}</h1>
          <p className="text-gray-500 capitalize">{entity.type.toLowerCase()} • {entity.category || 'Uncategorized'}</p>
        </div>
        <div className="flex items-center space-x-3">
          {riskScore && (
            <div className={`px-4 py-2 rounded-lg border ${getRiskColor(riskScore.risk_level)}`}>
              <div className="text-xs uppercase font-medium">Risk Level</div>
              <div className="text-lg font-bold">{riskScore.risk_level}</div>
              <div className="text-xs">Score: {riskScore.overall_score.toFixed(1)}</div>
            </div>
          )}
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${entity.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
            {entity.is_active ? 'Active' : 'Inactive'}
          </span>
        </div>
      </div>

      {/* Main Info Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Entity Details */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Entity Information</h2>
          <dl className="grid grid-cols-2 gap-4">
            <div>
              <dt className="text-sm text-gray-500">Type</dt>
              <dd className="font-medium capitalize">{entity.type.toLowerCase()}</dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Country</dt>
              <dd className="font-medium">{entity.country_code || 'N/A'}</dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Category</dt>
              <dd className="font-medium">{entity.category || 'N/A'}</dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Subcategory</dt>
              <dd className="font-medium">{entity.subcategory || 'N/A'}</dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Criticality</dt>
              <dd className="font-medium">{getCriticalityLabel(entity.criticality)} ({entity.criticality}/5)</dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Created</dt>
              <dd className="font-medium">{new Date(entity.created_at).toLocaleDateString()}</dd>
            </div>
            {entity.aliases?.length > 0 && (
              <div className="col-span-2">
                <dt className="text-sm text-gray-500">Aliases</dt>
                <dd className="font-medium">{entity.aliases.join(', ')}</dd>
              </div>
            )}
            {entity.tags?.length > 0 && (
              <div className="col-span-2">
                <dt className="text-sm text-gray-500">Tags</dt>
                <dd className="flex flex-wrap gap-1 mt-1">
                  {entity.tags.map(tag => (
                    <span key={tag} className="px-2 py-0.5 bg-gray-100 text-gray-700 rounded text-sm">{tag}</span>
                  ))}
                </dd>
              </div>
            )}
            {entity.notes && (
              <div className="col-span-2">
                <dt className="text-sm text-gray-500">Notes</dt>
                <dd className="font-medium">{entity.notes}</dd>
              </div>
            )}
          </dl>
        </div>

        {/* Risk Breakdown */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Risk Analysis</h2>
          {riskScore ? (
            <div className="space-y-4">
              <div className="text-center p-4 rounded-lg bg-gray-50">
                <div className="text-3xl font-bold text-gray-900">{riskScore.overall_score.toFixed(1)}</div>
                <div className={`inline-block px-2 py-1 rounded text-sm font-medium mt-1 ${getRiskColor(riskScore.risk_level)}`}>
                  {riskScore.risk_level}
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Constraint Risk</span>
                  <span className="font-medium">{riskScore.constraint_score?.toFixed(1) || 'N/A'}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Dependency Risk</span>
                  <span className="font-medium">{riskScore.dependency_score?.toFixed(1) || 'N/A'}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Country Risk</span>
                  <span className="font-medium">{riskScore.country_score?.toFixed(1) || 'N/A'}</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center text-gray-500 py-8">
              <p>No risk score calculated</p>
              <button className="mt-2 text-primary-600 hover:underline text-sm">
                Calculate Risk
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Dependencies Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Outgoing Dependencies */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">
            Outgoing Dependencies ({outgoingDeps.length})
          </h2>
          {outgoingDeps.length > 0 ? (
            <div className="space-y-3">
              {outgoingDeps.map(dep => (
                <Link
                  key={dep.id}
                  to={`/entities/${dep.target_entity_id}`}
                  className="block p-3 border rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-medium text-primary-600">{dep.target_entity_name || 'Unknown Entity'}</div>
                      <div className="text-sm text-gray-500 capitalize">
                        {dep.relationship_type.toLowerCase().replace(/_/g, ' ')}
                      </div>
                    </div>
                    <div className="text-right">
                      <span className="text-xs bg-gray-100 px-2 py-1 rounded capitalize">{dep.layer.toLowerCase()}</span>
                      <div className="text-xs text-gray-500 mt-1">Criticality: {dep.criticality}/5</div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">No outgoing dependencies</p>
          )}
        </div>

        {/* Incoming Dependencies */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">
            Incoming Dependencies ({incomingDeps.length})
          </h2>
          {incomingDeps.length > 0 ? (
            <div className="space-y-3">
              {incomingDeps.map(dep => (
                <Link
                  key={dep.id}
                  to={`/entities/${dep.source_entity_id}`}
                  className="block p-3 border rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-medium text-primary-600">{dep.source_entity_name || 'Unknown Entity'}</div>
                      <div className="text-sm text-gray-500 capitalize">
                        {dep.relationship_type.toLowerCase().replace(/_/g, ' ')}
                      </div>
                    </div>
                    <div className="text-right">
                      <span className="text-xs bg-gray-100 px-2 py-1 rounded capitalize">{dep.layer.toLowerCase()}</span>
                      <div className="text-xs text-gray-500 mt-1">Criticality: {dep.criticality}/5</div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">No incoming dependencies</p>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-end space-x-3">
        <Link
          to={`/dependencies?entity_id=${id}`}
          className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
        >
          View Dependency Graph
        </Link>
        <Link
          to={`/audit?resource_type=entity&resource_id=${id}`}
          className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
        >
          View Audit History
        </Link>
      </div>
    </div>
  )
}
