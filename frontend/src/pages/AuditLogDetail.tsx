import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { auditApi } from "../services/api";

interface AuditLog {
  id: string;
  user_id: string;
  user_email: string;
  action: string;
  resource_type: string;
  resource_id: string;
  resource_name: string;
  changes: Record<string, any>;
  context_data: Record<string, any>;
  ip_address: string;
  user_agent: string;
  created_at: string;
}

export default function AuditLogDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const {
    data: log,
    isLoading,
    error,
  } = useQuery<AuditLog>({
    queryKey: ["audit-log", id],
    queryFn: async () => {
      const response = await auditApi.get(id!);
      return response.data;
    },
    enabled: !!id,
  });

  const actionColors: Record<string, string> = {
    CREATE: "bg-green-100 text-green-800",
    UPDATE: "bg-blue-100 text-blue-800",
    DELETE: "bg-red-100 text-red-800",
    LOGIN: "bg-purple-100 text-purple-800",
    LOGOUT: "bg-gray-100 text-gray-800",
    VIEW: "bg-yellow-100 text-yellow-800",
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error || !log) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700">Failed to load audit log entry</p>
        <button
          onClick={() => navigate("/audit")}
          className="mt-2 text-red-600 underline"
        >
          Back to Audit Log
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <button
          onClick={() => navigate("/audit")}
          className="text-sm text-gray-500 hover:text-gray-700 mb-2 flex items-center"
        >
          ← Back to Audit Log
        </button>
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">Audit Log Entry</h1>
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium ${actionColors[log.action] || "bg-gray-100 text-gray-800"}`}
          >
            {log.action}
          </span>
        </div>
        <p className="text-gray-500 mt-1">
          {new Date(log.created_at).toLocaleString()}
        </p>
      </div>

      {/* Summary Card */}
      <div className="card mb-6">
        <h2 className="text-lg font-semibold mb-4">Summary</h2>
        <dl className="grid grid-cols-2 gap-4">
          <div>
            <dt className="text-sm text-gray-500">Action</dt>
            <dd className="font-medium">{log.action}</dd>
          </div>
          <div>
            <dt className="text-sm text-gray-500">Resource Type</dt>
            <dd className="font-medium capitalize">
              {log.resource_type?.toLowerCase()}
            </dd>
          </div>
          <div>
            <dt className="text-sm text-gray-500">Resource</dt>
            <dd className="font-medium">
              {log.resource_name || log.resource_id || "N/A"}
            </dd>
          </div>
          <div>
            <dt className="text-sm text-gray-500">User</dt>
            <dd className="font-medium">{log.user_email}</dd>
          </div>
          <div>
            <dt className="text-sm text-gray-500">Timestamp</dt>
            <dd className="font-medium">
              {new Date(log.created_at).toLocaleString()}
            </dd>
          </div>
          <div>
            <dt className="text-sm text-gray-500">IP Address</dt>
            <dd className="font-medium font-mono text-sm">
              {log.ip_address || "N/A"}
            </dd>
          </div>
        </dl>
      </div>

      {/* Changes */}
      {log.changes && Object.keys(log.changes).length > 0 && (
        <div className="card mb-6">
          <h2 className="text-lg font-semibold mb-4">Changes</h2>
          <div className="bg-gray-50 rounded-lg p-4 overflow-auto">
            <table className="min-w-full">
              <thead>
                <tr className="text-left text-sm text-gray-500">
                  <th className="pb-2 pr-4">Field</th>
                  <th className="pb-2 pr-4">Before</th>
                  <th className="pb-2">After</th>
                </tr>
              </thead>
              <tbody className="text-sm">
                {Object.entries(log.changes).map(
                  ([field, change]: [string, any]) => (
                    <tr key={field} className="border-t border-gray-200">
                      <td className="py-2 pr-4 font-medium">{field}</td>
                      <td className="py-2 pr-4 text-red-600">
                        {change.old !== undefined
                          ? typeof change.old === "object"
                            ? JSON.stringify(change.old)
                            : String(change.old)
                          : "-"}
                      </td>
                      <td className="py-2 text-green-600">
                        {change.new !== undefined
                          ? typeof change.new === "object"
                            ? JSON.stringify(change.new)
                            : String(change.new)
                          : "-"}
                      </td>
                    </tr>
                  ),
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Context Data */}
      {log.context_data && Object.keys(log.context_data).length > 0 && (
        <div className="card mb-6">
          <h2 className="text-lg font-semibold mb-4">Context Data</h2>
          <pre className="bg-gray-50 rounded-lg p-4 text-sm overflow-auto">
            {JSON.stringify(log.context_data, null, 2)}
          </pre>
        </div>
      )}

      {/* User Agent */}
      {log.user_agent && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">User Agent</h2>
          <p className="text-sm text-gray-600 font-mono break-all">
            {log.user_agent}
          </p>
        </div>
      )}
    </div>
  );
}
