import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { constraintsApi, entitiesApi } from "../services/api";

interface Constraint {
  id: string;
  name: string;
  description: string;
  type: string;
  severity: string;
  reference_code: string;
  source_document: string;
  external_url: string;
  applies_to_entity_types: string[];
  applies_to_countries: string[];
  applies_to_categories: string[];
  effective_date: string;
  expiry_date: string;
  review_date: string;
  risk_weight: number;
  requirements: Record<string, any>;
  is_mandatory: boolean;
  is_active: boolean;
  tags: string[];
  custom_data: Record<string, any>;
  created_at: string;
  updated_at: string;
}

interface Entity {
  id: string;
  name: string;
  type: string;
  country_code: string;
  category: string;
}

export default function ConstraintDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [constraint, setConstraint] = useState<Constraint | null>(null);
  const [affectedEntities, setAffectedEntities] = useState<Entity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (id) {
      loadConstraintData();
    }
  }, [id]);

  const loadConstraintData = async () => {
    try {
      setLoading(true);
      const constraintRes = await constraintsApi.get(id!);
      setConstraint(constraintRes.data);

      // Load entities that might be affected by this constraint
      try {
        const entitiesRes = await entitiesApi.list({ page_size: 100 });
        const allEntities = entitiesRes.data.items || [];

        // Filter entities based on constraint criteria
        const affected = allEntities.filter((entity: Entity) => {
          const typeMatch =
            constraintRes.data.applies_to_entity_types?.length === 0 ||
            constraintRes.data.applies_to_entity_types?.includes(entity.type);
          const countryMatch =
            constraintRes.data.applies_to_countries?.length === 0 ||
            constraintRes.data.applies_to_countries?.includes(
              entity.country_code,
            );
          const categoryMatch =
            constraintRes.data.applies_to_categories?.length === 0 ||
            constraintRes.data.applies_to_categories?.includes(entity.category);
          return typeMatch && countryMatch && categoryMatch;
        });
        setAffectedEntities(affected.slice(0, 10)); // Show top 10
      } catch {
        // Entities might not load
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load constraint");
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case "critical":
        return "bg-red-100 text-red-800 border-red-200";
      case "high":
        return "bg-orange-100 text-orange-800 border-orange-200";
      case "medium":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "low":
        return "bg-green-100 text-green-800 border-green-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      policy: "bg-blue-100 text-blue-800",
      regulation: "bg-purple-100 text-purple-800",
      compliance: "bg-green-100 text-green-800",
      contractual: "bg-yellow-100 text-yellow-800",
      operational: "bg-orange-100 text-orange-800",
      financial: "bg-red-100 text-red-800",
      security: "bg-gray-100 text-gray-800",
    };
    return colors[type?.toLowerCase()] || "bg-gray-100 text-gray-800";
  };

  const isExpiringSoon = (date: string) => {
    if (!date) return false;
    const expiry = new Date(date);
    const thirtyDaysFromNow = new Date();
    thirtyDaysFromNow.setDate(thirtyDaysFromNow.getDate() + 30);
    return expiry <= thirtyDaysFromNow && expiry >= new Date();
  };

  const isExpired = (date: string) => {
    if (!date) return false;
    return new Date(date) < new Date();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error || !constraint) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700">{error || "Constraint not found"}</p>
        <button
          onClick={() => navigate("/constraints")}
          className="mt-2 text-red-600 underline"
        >
          Back to Constraints
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <button
            onClick={() => navigate("/constraints")}
            className="text-sm text-gray-500 hover:text-gray-700 mb-2 flex items-center"
          >
            ← Back to Constraints
          </button>
          <h1 className="text-2xl font-bold text-gray-900">
            {constraint.name}
          </h1>
          <div className="flex items-center gap-2 mt-1">
            <span
              className={`px-2 py-0.5 rounded text-xs font-medium capitalize ${getTypeColor(constraint.type)}`}
            >
              {constraint.type}
            </span>
            {constraint.reference_code && (
              <span className="text-gray-500 text-sm">
                Ref: {constraint.reference_code}
              </span>
            )}
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <div
            className={`px-4 py-2 rounded-lg border ${getSeverityColor(constraint.severity)}`}
          >
            <div className="text-xs uppercase font-medium">Severity</div>
            <div className="text-lg font-bold capitalize">
              {constraint.severity}
            </div>
          </div>
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium ${constraint.is_active ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"}`}
          >
            {constraint.is_active ? "Active" : "Inactive"}
          </span>
          {constraint.is_mandatory && (
            <span className="px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
              Mandatory
            </span>
          )}
        </div>
      </div>

      {/* Expiry Warning */}
      {constraint.expiry_date &&
        isExpiringSoon(constraint.expiry_date) &&
        !isExpired(constraint.expiry_date) && (
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
            <p className="text-orange-700 font-medium">
              This constraint expires on{" "}
              {new Date(constraint.expiry_date).toLocaleDateString()}
            </p>
          </div>
        )}
      {constraint.expiry_date && isExpired(constraint.expiry_date) && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700 font-medium">
            This constraint expired on{" "}
            {new Date(constraint.expiry_date).toLocaleDateString()}
          </p>
        </div>
      )}

      {/* Main Info Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Constraint Details */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Constraint Details</h2>

          {constraint.description && (
            <div className="mb-4">
              <h3 className="text-sm text-gray-500 mb-1">Description</h3>
              <p className="text-gray-900">{constraint.description}</p>
            </div>
          )}

          <dl className="grid grid-cols-2 gap-4">
            <div>
              <dt className="text-sm text-gray-500">Type</dt>
              <dd className="font-medium capitalize">{constraint.type}</dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Severity</dt>
              <dd className="font-medium capitalize">{constraint.severity}</dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Risk Weight</dt>
              <dd className="font-medium">{constraint.risk_weight}/10</dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Mandatory</dt>
              <dd className="font-medium">
                {constraint.is_mandatory ? "Yes" : "No"}
              </dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Effective Date</dt>
              <dd className="font-medium">
                {constraint.effective_date
                  ? new Date(constraint.effective_date).toLocaleDateString()
                  : "N/A"}
              </dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Expiry Date</dt>
              <dd className="font-medium">
                {constraint.expiry_date
                  ? new Date(constraint.expiry_date).toLocaleDateString()
                  : "No expiry"}
              </dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Review Date</dt>
              <dd className="font-medium">
                {constraint.review_date
                  ? new Date(constraint.review_date).toLocaleDateString()
                  : "Not set"}
              </dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Created</dt>
              <dd className="font-medium">
                {new Date(constraint.created_at).toLocaleDateString()}
              </dd>
            </div>
            {constraint.source_document && (
              <div className="col-span-2">
                <dt className="text-sm text-gray-500">Source Document</dt>
                <dd className="font-medium">{constraint.source_document}</dd>
              </div>
            )}
            {constraint.external_url && (
              <div className="col-span-2">
                <dt className="text-sm text-gray-500">External URL</dt>
                <dd>
                  <a
                    href={constraint.external_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary-600 hover:underline"
                  >
                    {constraint.external_url}
                  </a>
                </dd>
              </div>
            )}
            {constraint.tags?.length > 0 && (
              <div className="col-span-2">
                <dt className="text-sm text-gray-500">Tags</dt>
                <dd className="flex flex-wrap gap-1 mt-1">
                  {constraint.tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-0.5 bg-gray-100 text-gray-700 rounded text-sm"
                    >
                      {tag}
                    </span>
                  ))}
                </dd>
              </div>
            )}
          </dl>
        </div>

        {/* Applicability */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Applicability</h2>
          <div className="space-y-4">
            <div>
              <h3 className="text-sm text-gray-500 mb-2">Entity Types</h3>
              {constraint.applies_to_entity_types?.length > 0 ? (
                <div className="flex flex-wrap gap-1">
                  {constraint.applies_to_entity_types.map((type) => (
                    <span
                      key={type}
                      className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-sm capitalize"
                    >
                      {type.toLowerCase()}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-sm">All entity types</p>
              )}
            </div>
            <div>
              <h3 className="text-sm text-gray-500 mb-2">Countries</h3>
              {constraint.applies_to_countries?.length > 0 ? (
                <div className="flex flex-wrap gap-1">
                  {constraint.applies_to_countries.map((country) => (
                    <span
                      key={country}
                      className="px-2 py-0.5 bg-green-100 text-green-700 rounded text-sm"
                    >
                      {country}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-sm">All countries</p>
              )}
            </div>
            <div>
              <h3 className="text-sm text-gray-500 mb-2">Categories</h3>
              {constraint.applies_to_categories?.length > 0 ? (
                <div className="flex flex-wrap gap-1">
                  {constraint.applies_to_categories.map((cat) => (
                    <span
                      key={cat}
                      className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded text-sm"
                    >
                      {cat}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-sm">All categories</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Requirements Section */}
      {constraint.requirements &&
        Object.keys(constraint.requirements).length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Requirements</h2>
            <pre className="bg-gray-50 p-4 rounded-lg text-sm overflow-auto">
              {JSON.stringify(constraint.requirements, null, 2)}
            </pre>
          </div>
        )}

      {/* Affected Entities */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">
          Potentially Affected Entities ({affectedEntities.length})
        </h2>
        {affectedEntities.length > 0 ? (
          <div className="space-y-3">
            {affectedEntities.map((entity) => (
              <Link
                key={entity.id}
                to={`/entities/${entity.id}`}
                className="block p-3 border rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="flex justify-between items-center">
                  <div>
                    <div className="font-medium text-primary-600">
                      {entity.name}
                    </div>
                    <div className="text-sm text-gray-500">
                      {entity.type} • {entity.country_code || "N/A"} •{" "}
                      {entity.category || "Uncategorized"}
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">
            No entities match the constraint criteria
          </p>
        )}
      </div>

      {/* Actions */}
      <div className="flex justify-end space-x-3">
        <Link
          to={`/audit?resource_type=constraint&resource_id=${id}`}
          className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
        >
          View Audit History
        </Link>
      </div>
    </div>
  );
}
