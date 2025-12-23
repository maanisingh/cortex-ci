import { useQuery } from '@tanstack/react-query'
import { PlusIcon, PlayIcon } from '@heroicons/react/24/outline'
import { scenariosApi } from '../services/api'

export default function Scenarios() {
  const { data, isLoading } = useQuery({
    queryKey: ['scenarios'],
    queryFn: async () => {
      const response = await scenariosApi.list()
      return response.data
    },
  })

  const statusColors: Record<string, string> = {
    draft: 'bg-gray-100 text-gray-800',
    running: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
    archived: 'bg-purple-100 text-purple-800',
  }

  const typeLabels: Record<string, string> = {
    entity_sanctioned: 'Entity Sanctioned',
    country_embargo: 'Country Embargo',
    supplier_unavailable: 'Supplier Unavailable',
    financial_restriction: 'Financial Restriction',
    regulatory_change: 'Regulatory Change',
    custom: 'Custom',
  }

  return (
    <div>
      <div className="sm:flex sm:items-center mb-6">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900">Scenario Simulation</h1>
          <p className="mt-2 text-sm text-gray-700">
            What-if analysis and stress testing
          </p>
        </div>
        <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
          <button type="button" className="btn-primary">
            <PlusIcon className="h-5 w-5 mr-2" />
            New Scenario
          </button>
        </div>
      </div>

      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="table-header">Name</th>
                <th className="table-header">Type</th>
                <th className="table-header">Status</th>
                <th className="table-header">Created</th>
                <th className="table-header">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {isLoading ? (
                <tr>
                  <td colSpan={5} className="px-6 py-4 text-center text-gray-500">
                    Loading...
                  </td>
                </tr>
              ) : data?.items?.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-4 text-center text-gray-500">
                    No scenarios found. Create one to start simulating.
                  </td>
                </tr>
              ) : (
                data?.items?.map((scenario: any) => (
                  <tr key={scenario.id} className="hover:bg-gray-50">
                    <td className="table-cell">
                      <div className="font-medium">{scenario.name}</div>
                      {scenario.description && (
                        <div className="text-xs text-gray-500 truncate max-w-xs">
                          {scenario.description}
                        </div>
                      )}
                    </td>
                    <td className="table-cell">
                      {typeLabels[scenario.type] || scenario.type}
                    </td>
                    <td className="table-cell">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          statusColors[scenario.status] || 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {scenario.status}
                      </span>
                    </td>
                    <td className="table-cell text-gray-500">
                      {new Date(scenario.created_at).toLocaleDateString()}
                    </td>
                    <td className="table-cell">
                      {scenario.status === 'draft' && (
                        <button
                          className="text-primary-600 hover:text-primary-900 text-sm flex items-center"
                          onClick={() => scenariosApi.run(scenario.id)}
                        >
                          <PlayIcon className="h-4 w-4 mr-1" />
                          Run
                        </button>
                      )}
                      {scenario.status === 'completed' && (
                        <button className="text-primary-600 hover:text-primary-900 text-sm">
                          View Results
                        </button>
                      )}
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
