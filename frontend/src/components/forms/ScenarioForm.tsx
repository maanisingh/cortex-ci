import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Modal from "../common/Modal";
import { scenariosApi, entitiesApi } from "../../services/api";

interface ScenarioFormProps {
  isOpen: boolean;
  onClose: () => void;
  scenario?: any;
}

const scenarioTypes = [
  { value: "entity_sanctioned", label: "Entity Sanctioned" },
  { value: "country_embargo", label: "Country Embargo" },
  { value: "supplier_unavailable", label: "Supplier Unavailable" },
  { value: "financial_restriction", label: "Financial Restriction" },
  { value: "regulatory_change", label: "Regulatory Change" },
  { value: "custom", label: "Custom Scenario" },
];

export default function ScenarioForm({
  isOpen,
  onClose,
  scenario,
}: ScenarioFormProps) {
  const queryClient = useQueryClient();
  const isEdit = !!scenario;

  const [formData, setFormData] = useState({
    name: "",
    description: "",
    type: "entity_sanctioned",
    trigger_entity_id: "",
    affected_countries: "",
    affected_entity_types: "",
  });

  const [error, setError] = useState("");

  // Fetch entities for dropdown
  const { data: entities } = useQuery({
    queryKey: ["entities-list"],
    queryFn: async () => {
      const response = await entitiesApi.list({ page_size: 200 });
      return response.data.items || [];
    },
  });

  useEffect(() => {
    if (scenario) {
      setFormData({
        name: scenario.name || "",
        description: scenario.description || "",
        type: scenario.type || "entity_sanctioned",
        trigger_entity_id: scenario.trigger_entity_id || "",
        affected_countries: scenario.affected_countries?.join(", ") || "",
        affected_entity_types: scenario.affected_entity_types?.join(", ") || "",
      });
    } else {
      setFormData({
        name: "",
        description: "",
        type: "entity_sanctioned",
        trigger_entity_id: "",
        affected_countries: "",
        affected_entity_types: "",
      });
    }
    setError("");
  }, [scenario, isOpen]);

  const mutation = useMutation({
    mutationFn: async (data: any) => {
      if (isEdit) {
        return scenariosApi.update(scenario.id, data);
      }
      return scenariosApi.create(data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scenarios"] });
      onClose();
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || "Failed to save scenario");
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    const payload = {
      ...formData,
      affected_countries: formData.affected_countries
        ? formData.affected_countries
            .split(",")
            .map((s) => s.trim())
            .filter(Boolean)
        : [],
      affected_entity_types: formData.affected_entity_types
        ? formData.affected_entity_types
            .split(",")
            .map((s) => s.trim())
            .filter(Boolean)
        : [],
      trigger_entity_id: formData.trigger_entity_id || null,
      description: formData.description || null,
    };

    mutation.mutate(payload);
  };

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >,
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const selectedType = scenarioTypes.find((t) => t.value === formData.type);

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEdit ? "Edit Scenario" : "Create New Scenario"}
      size="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <div className="grid grid-cols-2 gap-4">
          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Scenario Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="e.g., Supplier X Sanctioned"
            />
          </div>

          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Scenario Type <span className="text-red-500">*</span>
            </label>
            <select
              name="type"
              value={formData.type}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            >
              {scenarioTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
            <p className="mt-1 text-sm text-gray-500">
              {selectedType?.value === "entity_sanctioned" &&
                "Simulate what happens if a specific entity is sanctioned"}
              {selectedType?.value === "country_embargo" &&
                "Simulate impact of embargo on specified countries"}
              {selectedType?.value === "supplier_unavailable" &&
                "Simulate supply chain disruption from supplier loss"}
              {selectedType?.value === "financial_restriction" &&
                "Simulate impact of financial restrictions"}
              {selectedType?.value === "regulatory_change" &&
                "Simulate impact of regulatory changes"}
              {selectedType?.value === "custom" &&
                "Create a custom scenario with specific parameters"}
            </p>
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
              placeholder="Describe the scenario and its expected impact"
            />
          </div>

          {(formData.type === "entity_sanctioned" ||
            formData.type === "supplier_unavailable") && (
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Trigger Entity
              </label>
              <select
                name="trigger_entity_id"
                value={formData.trigger_entity_id}
                onChange={handleChange}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              >
                <option value="">Select entity to simulate impact</option>
                {entities?.map((entity: any) => (
                  <option key={entity.id} value={entity.id}>
                    {entity.name} ({entity.type})
                  </option>
                ))}
              </select>
              <p className="mt-1 text-sm text-gray-500">
                The entity that will be affected in this scenario
              </p>
            </div>
          )}

          {(formData.type === "country_embargo" ||
            formData.type === "regulatory_change") && (
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Affected Countries (comma-separated)
              </label>
              <input
                type="text"
                name="affected_countries"
                value={formData.affected_countries}
                onChange={handleChange}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                placeholder="e.g., RUS, IRN, PRK"
              />
              <p className="mt-1 text-sm text-gray-500">
                ISO 3-letter country codes of affected countries
              </p>
            </div>
          )}

          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Affected Entity Types (comma-separated)
            </label>
            <input
              type="text"
              name="affected_entity_types"
              value={formData.affected_entity_types}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="e.g., ORGANIZATION, INDIVIDUAL (leave empty for all)"
            />
          </div>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4">
          <h4 className="text-sm font-medium text-blue-800 mb-1">
            What happens next?
          </h4>
          <p className="text-sm text-blue-600">
            After creating this scenario, you can run it to simulate the impact.
            The system will analyze dependency chains and calculate how many
            entities would be affected, their risk changes, and provide
            recommendations.
          </p>
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
                ? "Update Scenario"
                : "Create Scenario"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
