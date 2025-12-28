import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { PlusIcon, MagnifyingGlassIcon } from "@heroicons/react/24/outline";
import { constraintsApi } from "../services/api";
import ConstraintForm from "../components/forms/ConstraintForm";
import { useLanguage } from "../contexts/LanguageContext";

export default function Constraints() {
  const { t } = useLanguage();
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editConstraint, setEditConstraint] = useState<any>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["constraints", search],
    queryFn: async () => {
      const response = await constraintsApi.list({
        page: 1,
        search: search || undefined,
      });
      return response.data;
    },
  });

  const { data: summary } = useQuery({
    queryKey: ["constraints-summary"],
    queryFn: async () => {
      const response = await constraintsApi.summary();
      return response.data;
    },
  });

  const typeColors: Record<string, string> = {
    policy: "bg-blue-100 text-blue-800",
    regulation: "bg-purple-100 text-purple-800",
    compliance: "bg-green-100 text-green-800",
    contractual: "bg-yellow-100 text-yellow-800",
    operational: "bg-orange-100 text-orange-800",
    financial: "bg-red-100 text-red-800",
    security: "bg-gray-100 text-gray-800",
  };

  const severityColors: Record<string, string> = {
    low: "bg-green-100 text-green-800",
    medium: "bg-yellow-100 text-yellow-800",
    high: "bg-orange-100 text-orange-800",
    critical: "bg-red-100 text-red-800",
  };

  return (
    <div>
      <div className="sm:flex sm:items-center mb-6">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{t("controls")}</h1>
          <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
            {t("controlsDescription")}
          </p>
        </div>
        <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
          <button
            type="button"
            className="btn-primary"
            onClick={() => {
              setEditConstraint(null);
              setShowForm(true);
            }}
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            {t("addControl")}
          </button>
        </div>
      </div>

      <ConstraintForm
        isOpen={showForm}
        onClose={() => {
          setShowForm(false);
          setEditConstraint(null);
        }}
        constraint={editConstraint}
      />

      {/* Summary Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-4 mb-6">
        <div className="card">
          <dt className="text-sm font-medium text-gray-500">
            {t("totalControls")}
          </dt>
          <dd className="mt-1 text-3xl font-semibold text-gray-900">
            {summary?.total || 0}
          </dd>
        </div>
        <div className="card">
          <dt className="text-sm font-medium text-gray-500">{t("mandatory")}</dt>
          <dd className="mt-1 text-3xl font-semibold text-gray-900">
            {summary?.mandatory || 0}
          </dd>
        </div>
        <div className="card border-l-4 border-orange-400">
          <dt className="text-sm font-medium text-gray-500">{t("expiringSoon")}</dt>
          <dd className="mt-1 text-3xl font-semibold text-orange-600">
            {summary?.expiring_soon || 0}
          </dd>
        </div>
        <div className="card">
          <dt className="text-sm font-medium text-gray-500">{t("active")}</dt>
          <dd className="mt-1 text-3xl font-semibold text-green-600">
            {summary?.active || 0}
          </dd>
        </div>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={t("searchControls")}
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
                <th className="table-header">{t("name")}</th>
                <th className="table-header">{t("type")}</th>
                <th className="table-header">{t("severity")}</th>
                <th className="table-header">{t("effective")}</th>
                <th className="table-header">{t("expires")}</th>
                <th className="table-header">{t("actions")}</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {isLoading ? (
                <tr>
                  <td
                    colSpan={6}
                    className="px-6 py-4 text-center text-gray-500"
                  >
                    {t("loading")}
                  </td>
                </tr>
              ) : data?.items?.length === 0 ? (
                <tr>
                  <td
                    colSpan={6}
                    className="px-6 py-4 text-center text-gray-500"
                  >
                    {t("noControlsFound")}
                  </td>
                </tr>
              ) : (
                data?.items?.map((constraint: any) => (
                  <tr
                    key={constraint.id}
                    className="hover:bg-gray-50 cursor-pointer"
                    onClick={() =>
                      (window.location.href = `/constraints/${constraint.id}`)
                    }
                  >
                    <td className="table-cell">
                      <Link
                        to={`/constraints/${constraint.id}`}
                        className="font-medium text-primary-600 hover:text-primary-800"
                      >
                        {constraint.name}
                      </Link>
                      {constraint.reference_code && (
                        <div className="text-xs text-gray-500">
                          {t("ref")}: {constraint.reference_code}
                        </div>
                      )}
                    </td>
                    <td className="table-cell">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${
                          typeColors[constraint.type?.toLowerCase()] ||
                          "bg-gray-100 text-gray-800"
                        }`}
                      >
                        {constraint.type}
                      </span>
                    </td>
                    <td className="table-cell">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${
                          severityColors[constraint.severity?.toLowerCase()] ||
                          "bg-gray-100 text-gray-800"
                        }`}
                      >
                        {constraint.severity}
                      </span>
                    </td>
                    <td className="table-cell text-gray-500">
                      {constraint.effective_date
                        ? new Date(
                            constraint.effective_date,
                          ).toLocaleDateString()
                        : "-"}
                    </td>
                    <td className="table-cell text-gray-500">
                      {constraint.expiry_date
                        ? new Date(constraint.expiry_date).toLocaleDateString()
                        : t("noExpiry")}
                    </td>
                    <td className="table-cell">
                      <Link
                        to={`/constraints/${constraint.id}`}
                        className="text-primary-600 hover:text-primary-900 text-sm"
                      >
                        {t("viewDetails")}
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
  );
}
