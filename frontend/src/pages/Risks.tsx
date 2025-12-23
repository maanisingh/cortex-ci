import { useQuery } from '@tanstack/react-query'
import { risksApi } from '../services/api'

export default function Risks() {
  const { data: summary } = useQuery({
    queryKey: ['risk-summary'],
    queryFn: async () => {
      const response = await risksApi.summary()
      return response.data
    },
  })

  const riskColors: Record<string, string> = {
    CRITICAL: 'bg-red-100 text-red-800 border-red-200',
    HIGH: 'bg-orange-100 text-orange-800 border-orange-200',
    MEDIUM: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    LOW: 'bg-green-100 text-green-800 border-green-200',
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
            className="btn-primary"
            onClick={() => risksApi.calculate({ force_recalculate: true })}
          >
            Recalculate All
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-6">
        {['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((level) => (
          <div key={level} className={`card border-2 ${riskColors[level]}`}>
            <dt className="text-sm font-medium">{level}</dt>
            <dd className="mt-1 text-3xl font-semibold">
              {summary?.[`${level.toLowerCase()}_count`] || 0}
            </dd>
          </div>
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
        <div className="mt-4 w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-primary-600 h-2 rounded-full"
            style={{ width: `${summary?.average_score || 0}%` }}
          />
        </div>
      </div>

      {/* Placeholder for risk table */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Entities by Risk Level</h3>
        <p className="text-gray-500">
          Risk details would be displayed here with entity breakdown, justifications, and trend indicators.
        </p>
      </div>
    </div>
  )
}
