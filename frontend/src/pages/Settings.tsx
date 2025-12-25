import { useQuery } from "@tanstack/react-query";
import { adminApi } from "../services/api";
import { useAuthStore } from "../stores/authStore";

export default function Settings() {
  const { user } = useAuthStore();

  const { data: settings } = useQuery({
    queryKey: ["settings"],
    queryFn: async () => {
      const response = await adminApi.settings.get();
      return response.data;
    },
    enabled: user?.role === "admin",
  });

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="mt-2 text-sm text-gray-700">
          System configuration and preferences
        </p>
      </div>

      {/* User Profile */}
      <div className="card mb-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Profile</h3>
        <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <dt className="text-sm font-medium text-gray-500">Full Name</dt>
            <dd className="mt-1 text-sm text-gray-900">{user?.full_name}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Email</dt>
            <dd className="mt-1 text-sm text-gray-900">{user?.email}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Role</dt>
            <dd className="mt-1 text-sm text-gray-900 capitalize">
              {user?.role}
            </dd>
          </div>
        </dl>
      </div>

      {/* Risk Weights (Admin only) */}
      {user?.role === "admin" && settings && (
        <div className="card mb-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Risk Calculation Weights
          </h3>
          <p className="text-sm text-gray-500 mb-4">
            Configure how different factors contribute to overall risk scores
          </p>
          <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {Object.entries(settings.risk_weights || {}).map(([key, value]) => (
              <div key={key}>
                <dt className="text-sm font-medium text-gray-500 capitalize">
                  {key.replace("_", " ")}
                </dt>
                <dd className="mt-1">
                  <div className="flex items-center">
                    <span className="text-2xl font-semibold text-gray-900">
                      {((value as number) * 100).toFixed(0)}%
                    </span>
                  </div>
                </dd>
              </div>
            ))}
          </dl>
        </div>
      )}

      {/* Tenant Info (Admin only) */}
      {user?.role === "admin" && settings && (
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Organization
          </h3>
          <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">Tenant Name</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {settings.tenant_name}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Tenant ID</dt>
              <dd className="mt-1 text-sm text-gray-500 font-mono text-xs">
                {settings.tenant_id}
              </dd>
            </div>
          </dl>
        </div>
      )}
    </div>
  );
}
