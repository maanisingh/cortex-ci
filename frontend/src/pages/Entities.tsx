import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { PlusIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline'
import { entitiesApi } from '../services/api'
import EntityForm from '../components/forms/EntityForm'

export default function Entities() {
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [showForm, setShowForm] = useState(false)
  const [editEntity, setEditEntity] = useState<any>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['entities', page, search],
    queryFn: async () => {
      const response = await entitiesApi.list({ page, page_size: 20, search: search || undefined })
      return response.data
    },
  })

  const typeColors: Record<string, string> = {
    organization: 'bg-blue-100 text-blue-800',
    individual: 'bg-purple-100 text-purple-800',
    location: 'bg-green-100 text-green-800',
    financial: 'bg-yellow-100 text-yellow-800',
  }

  return (
    <div>
      <div className="sm:flex sm:items-center mb-6">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900">Entities</h1>
          <p className="mt-2 text-sm text-gray-700">
            Organizations, individuals, and other monitored entities
          </p>
        </div>
        <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
          <button type="button" className="btn-primary" onClick={() => { setEditEntity(null); setShowForm(true); }}>
            <PlusIcon className="h-5 w-5 mr-2" />
            Add Entity
          </button>
        </div>
      </div>

      <EntityForm
        isOpen={showForm}
        onClose={() => { setShowForm(false); setEditEntity(null); }}
        entity={editEntity}
      />

      {/* Search */}
      <div className="mb-6">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search entities..."
            className="pl-10 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          />
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="table-header">Name</th>
                <th className="table-header">Type</th>
                <th className="table-header">Country</th>
                <th className="table-header">Criticality</th>
                <th className="table-header">Created</th>
                <th className="table-header">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                    Loading...
                  </td>
                </tr>
              ) : data?.items?.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                    No entities found
                  </td>
                </tr>
              ) : (
                data?.items?.map((entity: any) => (
                  <tr key={entity.id} className="hover:bg-gray-50 cursor-pointer" onClick={() => window.location.href = `/entities/${entity.id}`}>
                    <td className="table-cell">
                      <Link to={`/entities/${entity.id}`} className="font-medium text-primary-600 hover:text-primary-800">
                        {entity.name}
                      </Link>
                    </td>
                    <td className="table-cell">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          typeColors[entity.type?.toLowerCase()] || 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {entity.type}
                      </span>
                    </td>
                    <td className="table-cell">{entity.country_code || '-'}</td>
                    <td className="table-cell">
                      <div className="flex items-center">
                        {[1, 2, 3, 4, 5].map((n) => (
                          <div
                            key={n}
                            className={`w-2 h-2 rounded-full mr-1 ${
                              n <= entity.criticality ? 'bg-primary-500' : 'bg-gray-200'
                            }`}
                          />
                        ))}
                      </div>
                    </td>
                    <td className="table-cell text-gray-500">
                      {new Date(entity.created_at).toLocaleDateString()}
                    </td>
                    <td className="table-cell">
                      <Link to={`/entities/${entity.id}`} className="text-primary-600 hover:text-primary-900 text-sm">
                        View Details
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {data && data.pages > 1 && (
          <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
            <div className="flex-1 flex justify-between sm:hidden">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="btn-secondary"
              >
                Previous
              </button>
              <button
                onClick={() => setPage((p) => Math.min(data.pages, p + 1))}
                disabled={page === data.pages}
                className="btn-secondary"
              >
                Next
              </button>
            </div>
            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-gray-700">
                  Showing page <span className="font-medium">{page}</span> of{' '}
                  <span className="font-medium">{data.pages}</span> ({data.total} total)
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="btn-secondary"
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage((p) => Math.min(data.pages, p + 1))}
                  disabled={page === data.pages}
                  className="btn-secondary"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
