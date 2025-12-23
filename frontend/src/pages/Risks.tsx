import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { ArrowPathIcon, ChevronUpIcon, ChevronDownIcon } from '@heroicons/react/24/outline'
import { risksApi, entitiesApi } from '../services/api'

interface EntityWithRisk {
  id: string
  name: string
  type: string
  country_code: string
  category: string
  criticality: number
  risk_score?: {
    overall_score: number
    risk_level: string
    constraint_score: number
    dependency_score: number
    country_score: number
  }
}

export default function Risks() {
  const queryClient = useQueryClient()
  const [selectedLevel, setSelectedLevel] = useState<string | null>(null)
  const [sortBy, setSortBy] = useState<'score' | 'name'>('score')
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc')

  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['risk-summary'],
    queryFn: async () => {
      const response = await risksApi.summary()
      return response.data
    },
  })

  const { data: entities, isLoading: entitiesLoading } = useQuery({
    queryKey: ['entities-with-risk'],
    queryFn: async () => {
      const response = await entitiesApi.list({ page_size: 100 })
      const entitiesData = response.data.items || []

      // Fetch risk scores for each entity
      const withRisks = await Promise.all(
        entitiesData.map(async (entity: any) => {
          try {
            const riskRes = await risksApi.entityRisk(entity.id)
            return { ...entity, risk_score: riskRes.data }
          } catch {
            return { ...entity, risk_score: null }
          }
        })
      )
      return withRisks
    },
  })

  const recalculateMutation = useMutation({
    mutationFn: () => risksApi.calculate({ force_recalculate: true }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['risk-summary'] })
      queryClient.invalidateQueries({ queryKey: ['entities-with-risk'] })
    },
  })

  const riskColors: Record<string, string> = {
    critical: 'bg-red-100 text-red-800 border-red-200',
    high: 'bg-orange-100 text-orange-800 border-orange-200',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    low: 'bg-green-100 text-green-800 border-green-200',
  }

  const riskBadgeColors: Record<string, string> = {
    critical: 'bg-red-500',
    high: 'bg-orange-500',
    medium: 'bg-yellow-500',
    low: 'bg-green-500',
  }

  // Filter and sort entities
  const filteredEntities = (entities || [])
    .filter((e: EntityWithRisk) => {
      if (!selectedLevel) return true
      return e.risk_score?.risk_level?.toLowerCase() === selectedLevel.toLowerCase()
    })
    .sort((a: EntityWithRisk, b: EntityWithRisk) => {
      if (sortBy === 'score') {
        const aScore = a.risk_score?.overall_score || 0
        const bScore = b.risk_score?.overall_score || 0
        return sortDir === 'desc' ? bScore - aScore : aScore - bScore
      } else {
        return sortDir === 'desc'
          ? b.name.localeCompare(a.name)
          : a.name.localeCompare(b.name)
      }
    })

  const toggleSort = (field: 'score' | 'name') => {
    if (sortBy === field) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(field)
      setSortDir('desc')
    }
  }

  const SortIcon = ({ field }: { field: 'score' | 'name' }) => {
    if (sortBy !== field) return null
    return sortDir === 'desc' ? (
      <ChevronDownIcon className="h-4 w-4 inline ml-1" />
    ) : (
      <ChevronUpIcon className="h-4 w-4 inline ml-1" />
    )
  }

  return (
    <div>
      <div className="sm:flex sm:items-center mb-6">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900">Risk Assessment</h1>
          <p className="mt-2 text-sm text-gray-700">
            Entity risk scores and analysis
          </p>
        </div>
        <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
          <button
            type="button"
            className="btn-primary flex items-center"
            onClick={() => recalculateMutation.mutate()}
            disabled={recalculateMutation.isPending}
          >
            <ArrowPathIcon className={`h-5 w-5 mr-2 ${recalculateMutation.isPending ? 'animate-spin' : ''}`} />
            {recalculateMutation.isPending ? 'Calculating...' : 'Recalculate All'}
          </button>
        </div>
      </div>

      {/* Summary Cards - Clickable filters */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-6">
        {['critical', 'high', 'medium', 'low'].map((level) => (
          <button
            key={level}
            onClick={() => setSelectedLevel(selectedLevel === level ? null : level)}
            className={`card border-2 text-left transition-all ${riskColors[level]} ${
              selectedLevel === level ? 'ring-2 ring-offset-2 ring-primary-500' : ''
            } ${selectedLevel && selectedLevel !== level ? 'opacity-50' : ''}`}
          >
            <dt className="text-sm font-medium uppercase">{level}</dt>
            <dd className="mt-1 text-3xl font-semibold">
              {summaryLoading ? '...' : summary?.[`${level}_count`] || 0}
            </dd>
            {selectedLevel === level && (
              <p className="text-xs mt-1">Click to clear filter</p>
            )}
          </button>
        ))}
      </div>

      {/* Average Score */}
      <div className="card mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-medium text-gray-900">Average Risk Score</h3>
            <p className="text-sm text-gray-500">
              Across {summary?.total_entities || 0} monitored entities
            </p>
          </div>
          <div className="text-4xl font-bold text-gray-900">
            {summary?.average_score?.toFixed(1) || '0.0'}
            <span className="text-lg font-normal text-gray-500">/100</span>
          </div>
        </div>
        <div className="mt-4 w-full bg-gray-200 rounded-full h-3">
          <div
            className="h-3 rounded-full transition-all duration-500"
            style={{
              width: `${summary?.average_score || 0}%`,
              backgroundColor:
                (summary?.average_score || 0) >= 75 ? '#ef4444' :
                (summary?.average_score || 0) >= 50 ? '#f97316' :
                (summary?.average_score || 0) >= 25 ? '#eab308' : '#22c55e'
            }}
          />
        </div>
      </div>

      {/* Entities Table */}
      <div className="card overflow-hidden">
        <div className="px-4 py-3 border-b border-gray-200 flex justify-between items-center">
          <h3 className="text-lg font-medium text-gray-900">
            Entities by Risk Level
            {selectedLevel && (
              <span className="ml-2 text-sm font-normal text-gray-500">
                (filtered: {selectedLevel})
              </span>
            )}
          </h3>
          <span className="text-sm text-gray-500">
            {filteredEntities.length} entities
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th
                  className="table-header cursor-pointer hover:bg-gray-100"
                  onClick={() => toggleSort('name')}
                >
                  Entity <SortIcon field="name" />
                </th>
                <th className="table-header">Type</th>
                <th className="table-header">Country</th>
                <th
                  className="table-header cursor-pointer hover:bg-gray-100"
                  onClick={() => toggleSort('score')}
                >
                  Risk Score <SortIcon field="score" />
                </th>
                <th className="table-header">Risk Level</th>
                <th className="table-header">Breakdown</th>
                <th className="table-header">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {entitiesLoading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-4 text-center text-gray-500">
                    <div className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600 mr-2"></div>
                      Loading entities and risk scores...
                    </div>
                  </td>
                </tr>
              ) : filteredEntities.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-4 text-center text-gray-500">
                    No entities found{selectedLevel ? ` with ${selectedLevel} risk level` : ''}
                  </td>
                </tr>
              ) : (
                filteredEntities.map((entity: EntityWithRisk) => (
                  <tr key={entity.id} className="hover:bg-gray-50">
                    <td className="table-cell">
                      <Link to={`/entities/${entity.id}`} className="font-medium text-primary-600 hover:text-primary-800">
                        {entity.name}
                      </Link>
                    </td>
                    <td className="table-cell text-sm text-gray-500 capitalize">
                      {entity.type?.toLowerCase()}
                    </td>
                    <td className="table-cell text-sm text-gray-500">
                      {entity.country_code || '-'}
                    </td>
                    <td className="table-cell">
                      {entity.risk_score ? (
                        <div className="flex items-center">
                          <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                            <div
                              className="h-2 rounded-full"
                              style={{
                                width: `${entity.risk_score.overall_score}%`,
                                backgroundColor: riskBadgeColors[entity.risk_score.risk_level?.toLowerCase()] || '#6b7280'
                              }}
                            />
                          </div>
                          <span className="text-sm font-medium">
                            {entity.risk_score.overall_score.toFixed(1)}
                          </span>
                        </div>
                      ) : (
                        <span className="text-gray-400 text-sm">Not calculated</span>
                      )}
                    </td>
                    <td className="table-cell">
                      {entity.risk_score ? (
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          riskColors[entity.risk_score.risk_level?.toLowerCase()] || 'bg-gray-100 text-gray-800'
                        }`}>
                          {entity.risk_score.risk_level}
                        </span>
                      ) : (
                        <span className="text-gray-400 text-sm">-</span>
                      )}
                    </td>
                    <td className="table-cell">
                      {entity.risk_score ? (
                        <div className="text-xs space-y-1">
                          <div className="flex justify-between">
                            <span className="text-gray-500">Constraint:</span>
                            <span className="font-medium">{entity.risk_score.constraint_score?.toFixed(1) || '-'}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-500">Dependency:</span>
                            <span className="font-medium">{entity.risk_score.dependency_score?.toFixed(1) || '-'}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-500">Country:</span>
                            <span className="font-medium">{entity.risk_score.country_score?.toFixed(1) || '-'}</span>
                          </div>
                        </div>
                      ) : (
                        <span className="text-gray-400 text-sm">-</span>
                      )}
                    </td>
                    <td className="table-cell">
                      <Link
                        to={`/entities/${entity.id}`}
                        className="text-primary-600 hover:text-primary-900 text-sm"
                      >
                        View Details
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
