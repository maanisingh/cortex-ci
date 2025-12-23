import { useQuery } from '@tanstack/react-query'
import { monitoringApi } from '../services/api'
import {
  CheckCircleIcon,
  ExclamationCircleIcon,
  ExclamationTriangleIcon,
  ServerIcon,
  ChartBarIcon,
  BellAlertIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline'

interface Alert {
  id: string
  type: string
  severity: string
  message: string
  entity_id?: string
  created_at: string
  is_acknowledged: boolean
}

export default function Monitoring() {
  const { data: dashboard, isLoading, refetch, isRefetching } = useQuery({
    queryKey: ['monitoring-dashboard'],
    queryFn: async () => {
      const response = await monitoringApi.dashboard()
      return response.data
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  const severityColors: Record<string, string> = {
    critical: 'bg-red-100 text-red-800 border-red-200',
    high: 'bg-orange-100 text-orange-800 border-orange-200',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    low: 'bg-blue-100 text-blue-800 border-blue-200',
  }

  const alertTypeLabels: Record<string, string> = {
    high_risk: 'High Risk Entity',
    pending_anomaly: 'Pending Anomaly',
    ai_pending_approval: 'AI Awaiting Approval',
    stale_data: 'Stale Data',
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <ArrowPathIcon className="h-8 w-8 animate-spin text-gray-400" />
      </div>
    )
  }

  return (
    <div>
      <div className="sm:flex sm:items-center mb-6">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900">System Monitoring</h1>
          <p className="mt-2 text-sm text-gray-700">
            Real-time system health, metrics, and alerts
          </p>
        </div>
        <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
          <button
            onClick={() => refetch()}
            className="btn-secondary"
            disabled={isRefetching}
          >
            <ArrowPathIcon className={`h-5 w-5 mr-2 ${isRefetching ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Health Status */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className={`card flex items-center ${
          dashboard?.health?.status === 'healthy' ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
        }`}>
          {dashboard?.health?.status === 'healthy' ? (
            <CheckCircleIcon className="h-10 w-10 text-green-500 mr-4" />
          ) : (
            <ExclamationCircleIcon className="h-10 w-10 text-red-500 mr-4" />
          )}
          <div>
            <div className="text-lg font-bold capitalize">{dashboard?.health?.status}</div>
            <div className="text-sm text-gray-600">System Status</div>
          </div>
        </div>

        <div className={`card flex items-center ${
          dashboard?.health?.database === 'connected' ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
        }`}>
          <ServerIcon className={`h-10 w-10 mr-4 ${
            dashboard?.health?.database === 'connected' ? 'text-green-500' : 'text-red-500'
          }`} />
          <div>
            <div className="text-lg font-bold capitalize">{dashboard?.health?.database}</div>
            <div className="text-sm text-gray-600">Database</div>
          </div>
        </div>

        <div className="card flex items-center">
          <ChartBarIcon className="h-10 w-10 text-primary-500 mr-4" />
          <div>
            <div className="text-lg font-bold">v{dashboard?.health?.version}</div>
            <div className="text-sm text-gray-600">Version</div>
          </div>
        </div>

        <div className={`card flex items-center ${
          dashboard?.alerts?.critical > 0 ? 'border-red-200 bg-red-50' : 'border-gray-200'
        }`}>
          <BellAlertIcon className={`h-10 w-10 mr-4 ${
            dashboard?.alerts?.critical > 0 ? 'text-red-500' : 'text-gray-400'
          }`} />
          <div>
            <div className="text-lg font-bold">{dashboard?.alerts?.unacknowledged || 0}</div>
            <div className="text-sm text-gray-600">Active Alerts</div>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="card mb-6">
        <h2 className="text-lg font-semibold mb-4">System Metrics</h2>
        <div className="grid grid-cols-5 gap-4">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-3xl font-bold text-primary-600">
              {dashboard?.metrics?.entities_count?.toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">Entities</div>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-3xl font-bold text-primary-600">
              {dashboard?.metrics?.constraints_count?.toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">Constraints</div>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-3xl font-bold text-primary-600">
              {dashboard?.metrics?.dependencies_count?.toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">Dependencies</div>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-3xl font-bold text-primary-600">
              {dashboard?.metrics?.risk_scores_count?.toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">Risk Scores</div>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-3xl font-bold text-primary-600">
              {dashboard?.metrics?.recent_audit_events?.toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">Audit (24h)</div>
          </div>
        </div>

        <div className="grid grid-cols-5 gap-4 mt-4">
          <div className="text-center p-4 bg-red-50 rounded-lg">
            <div className="text-3xl font-bold text-red-600">
              {dashboard?.metrics?.high_risk_entities?.toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">High Risk</div>
          </div>
          <div className="text-center p-4 bg-orange-50 rounded-lg">
            <div className="text-3xl font-bold text-orange-600">
              {dashboard?.metrics?.critical_constraints?.toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">Critical Constraints</div>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-3xl font-bold text-purple-600">
              {dashboard?.metrics?.scenario_chains_count?.toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">Scenario Chains</div>
          </div>
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-3xl font-bold text-blue-600">
              {dashboard?.metrics?.ai_analyses_count?.toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">AI Analyses</div>
          </div>
          <div className="text-center p-4 bg-yellow-50 rounded-lg">
            <div className="text-3xl font-bold text-yellow-600">
              {dashboard?.metrics?.pending_anomalies_count?.toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">Pending Anomalies</div>
          </div>
        </div>
      </div>

      {/* Alerts Section */}
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Active Alerts</h2>
          <div className="text-sm text-gray-500">
            {dashboard?.alerts?.total} total, {dashboard?.alerts?.critical} critical
          </div>
        </div>

        {!dashboard?.alerts?.recent?.length ? (
          <div className="text-center py-8 text-gray-500">
            <CheckCircleIcon className="h-12 w-12 mx-auto text-green-400 mb-2" />
            <p>No active alerts. System is operating normally.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {dashboard.alerts.recent.map((alert: Alert) => (
              <div
                key={alert.id}
                className={`p-4 rounded-lg border ${severityColors[alert.severity]}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start">
                    {alert.severity === 'critical' ? (
                      <ExclamationCircleIcon className="h-5 w-5 text-red-600 mr-2 mt-0.5" />
                    ) : (
                      <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600 mr-2 mt-0.5" />
                    )}
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{alertTypeLabels[alert.type] || alert.type}</span>
                        <span className={`px-2 py-0.5 rounded text-xs font-medium uppercase ${severityColors[alert.severity]}`}>
                          {alert.severity}
                        </span>
                      </div>
                      <p className="text-sm mt-1">{alert.message}</p>
                    </div>
                  </div>
                  <div className="text-xs text-gray-500">
                    {new Date(alert.created_at).toLocaleString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="text-xs text-gray-500 mt-4 text-right">
        Last updated: {dashboard?.generated_at ? new Date(dashboard.generated_at).toLocaleString() : 'N/A'}
      </div>
    </div>
  )
}
