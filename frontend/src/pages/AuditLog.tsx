import { useQuery } from "@tanstack/react-query";
import { auditApi } from "../services/api";

export default function AuditLog() {
  const { data, isLoading } = useQuery({
    queryKey: ["audit"],
    queryFn: async () => {
      const response = await auditApi.list({ page: 1 });
      return response.data;
    },
  });

  const actionColors: Record<string, string> = {
    login: "bg-green-100 text-green-800",
    logout: "bg-gray-100 text-gray-800",
    create: "bg-blue-100 text-blue-800",
    update: "bg-yellow-100 text-yellow-800",
    delete: "bg-red-100 text-red-800",
  };

  return (
    <div>
      <div className="sm:flex sm:items-center mb-6">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900">Audit Log</h1>
          <p className="mt-2 text-sm text-gray-700">
            Complete history of all actions in the system
          </p>
        </div>
        <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
          <button type="button" className="btn-secondary">
            Export
          </button>
        </div>
      </div>

      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="table-header">Timestamp</th>
                <th className="table-header">User</th>
                <th className="table-header">Action</th>
                <th className="table-header">Resource</th>
                <th className="table-header">Status</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {isLoading ? (
                <tr>
                  <td
                    colSpan={5}
                    className="px-6 py-4 text-center text-gray-500"
                  >
                    Loading...
                  </td>
                </tr>
              ) : data?.items?.length === 0 ? (
                <tr>
                  <td
                    colSpan={5}
                    className="px-6 py-4 text-center text-gray-500"
                  >
                    No audit entries found
                  </td>
                </tr>
              ) : (
                data?.items?.map((entry: any) => (
                  <tr key={entry.id} className="hover:bg-gray-50">
                    <td className="table-cell text-gray-500">
                      {new Date(entry.created_at).toLocaleString()}
                    </td>
                    <td className="table-cell">
                      <div className="font-medium">
                        {entry.user_email || "System"}
                      </div>
                      <div className="text-xs text-gray-500">
                        {entry.user_role}
                      </div>
                    </td>
                    <td className="table-cell">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          actionColors[entry.action?.split("_")[0]] ||
                          "bg-gray-100 text-gray-800"
                        }`}
                      >
                        {entry.action}
                      </span>
                    </td>
                    <td className="table-cell">
                      {entry.resource_type && (
                        <div>
                          <span className="text-gray-900">
                            {entry.resource_type}
                          </span>
                          {entry.resource_name && (
                            <span className="text-gray-500 text-xs block">
                              {entry.resource_name}
                            </span>
                          )}
                        </div>
                      )}
                    </td>
                    <td className="table-cell">
                      {entry.success ? (
                        <span className="text-green-600">Success</span>
                      ) : (
                        <span className="text-red-600">Failed</span>
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
  );
}
