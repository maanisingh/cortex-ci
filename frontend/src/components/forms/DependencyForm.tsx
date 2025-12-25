import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Modal from "../common/Modal";
import { dependenciesApi, entitiesApi } from "../../services/api";

interface DependencyFormProps {
  isOpen: boolean;
  onClose: () => void;
  dependency?: any;
  preselectedSourceId?: string;
  preselectedTargetId?: string;
}

const layers = ["OPERATIONAL", "FINANCIAL", "LEGAL", "ACADEMIC", "HUMAN"];
const relationshipTypes = [
  "SUPPLIES_TO",
  "SOURCES_FROM",
  "SUBSIDIARY_OF",
  "PARTNER_OF",
  "OWNS",
  "CONTROLS",
  "PROVIDES_SERVICE_TO",
  "RECEIVES_SERVICE_FROM",
  "TRANSACTS_WITH",
  "EMPLOYS",
  "CONTRACTS_WITH",
  "INVESTS_IN",
  "RECEIVES_INVESTMENT_FROM",
];

const criticalityOptions = [
  { value: 1, label: "Very Low" },
  { value: 2, label: "Low" },
  { value: 3, label: "Medium" },
  { value: 4, label: "High" },
  { value: 5, label: "Critical" },
];

export default function DependencyForm({
  isOpen,
  onClose,
  dependency,
  preselectedSourceId,
  preselectedTargetId,
}: DependencyFormProps) {
  const queryClient = useQueryClient();
  const isEdit = !!dependency;

  const [formData, setFormData] = useState({
    source_entity_id: "",
    target_entity_id: "",
    layer: "OPERATIONAL",
    relationship_type: "SUPPLIES_TO",
    criticality: 3,
    description: "",
    is_bidirectional: false,
  });

  const [error, setError] = useState("");

  // Fetch entities for dropdowns
  const { data: entities } = useQuery({
    queryKey: ["entities-list"],
    queryFn: async () => {
      const response = await entitiesApi.list({ page_size: 200 });
      return response.data.items || [];
    },
  });

  useEffect(() => {
    if (dependency) {
      setFormData({
        source_entity_id: dependency.source_entity_id || "",
        target_entity_id: dependency.target_entity_id || "",
        layer: dependency.layer || "OPERATIONAL",
        relationship_type: dependency.relationship_type || "SUPPLIES_TO",
        criticality: dependency.criticality || 3,
        description: dependency.description || "",
        is_bidirectional: dependency.is_bidirectional || false,
      });
    } else {
      setFormData({
        source_entity_id: preselectedSourceId || "",
        target_entity_id: preselectedTargetId || "",
        layer: "OPERATIONAL",
        relationship_type: "SUPPLIES_TO",
        criticality: 3,
        description: "",
        is_bidirectional: false,
      });
    }
    setError("");
  }, [dependency, isOpen, preselectedSourceId, preselectedTargetId]);

  const mutation = useMutation({
    mutationFn: async (data: any) => {
      if (isEdit) {
        return dependenciesApi.update(dependency.id, data);
      }
      return dependenciesApi.create(data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dependencies"] });
      queryClient.invalidateQueries({ queryKey: ["dependency-graph"] });
      onClose();
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || "Failed to save dependency");
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (formData.source_entity_id === formData.target_entity_id) {
      setError("Source and target entities must be different");
      return;
    }

    const payload = {
      ...formData,
      description: formData.description || null,
    };

    mutation.mutate(payload);
  };

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >,
  ) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]:
        type === "checkbox"
          ? (e.target as HTMLInputElement).checked
          : name === "criticality"
            ? parseInt(value)
            : value,
    }));
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEdit ? "Edit Dependency" : "Add New Dependency"}
      size="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Source Entity <span className="text-red-500">*</span>
            </label>
            <select
              name="source_entity_id"
              value={formData.source_entity_id}
              onChange={handleChange}
              required
              disabled={isEdit}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 disabled:bg-gray-100"
            >
              <option value="">Select source entity</option>
              {entities?.map((entity: any) => (
                <option key={entity.id} value={entity.id}>
                  {entity.name} ({entity.type})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Target Entity <span className="text-red-500">*</span>
            </label>
            <select
              name="target_entity_id"
              value={formData.target_entity_id}
              onChange={handleChange}
              required
              disabled={isEdit}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 disabled:bg-gray-100"
            >
              <option value="">Select target entity</option>
              {entities?.map((entity: any) => (
                <option key={entity.id} value={entity.id}>
                  {entity.name} ({entity.type})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Layer <span className="text-red-500">*</span>
            </label>
            <select
              name="layer"
              value={formData.layer}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            >
              {layers.map((layer) => (
                <option key={layer} value={layer}>
                  {layer}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Relationship Type <span className="text-red-500">*</span>
            </label>
            <select
              name="relationship_type"
              value={formData.relationship_type}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            >
              {relationshipTypes.map((type) => (
                <option key={type} value={type}>
                  {type.replace(/_/g, " ")}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Criticality
            </label>
            <select
              name="criticality"
              value={formData.criticality}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            >
              {criticalityOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label} ({opt.value}/5)
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center pt-6">
            <input
              type="checkbox"
              name="is_bidirectional"
              checked={formData.is_bidirectional}
              onChange={handleChange}
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label className="ml-2 block text-sm text-gray-700">
              Bidirectional relationship
            </label>
          </div>

          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows={3}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="Describe the relationship"
            />
          </div>
        </div>

        <div className="flex justify-end space-x-3 pt-4 border-t">
          <button type="button" onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button
            type="submit"
            disabled={mutation.isPending}
            className="btn-primary"
          >
            {mutation.isPending
              ? "Saving..."
              : isEdit
                ? "Update Dependency"
                : "Create Dependency"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
