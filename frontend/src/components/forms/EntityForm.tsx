import { useState, useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import Modal from "../common/Modal";
import { entitiesApi } from "../../services/api";

interface EntityFormProps {
  isOpen: boolean;
  onClose: () => void;
  entity?: any; // For edit mode
}

const entityTypes = ["ORGANIZATION", "INDIVIDUAL", "LOCATION", "FINANCIAL"];
const criticalityOptions = [
  { value: 1, label: "Very Low" },
  { value: 2, label: "Low" },
  { value: 3, label: "Medium" },
  { value: 4, label: "High" },
  { value: 5, label: "Critical" },
];

export default function EntityForm({
  isOpen,
  onClose,
  entity,
}: EntityFormProps) {
  const queryClient = useQueryClient();
  const isEdit = !!entity;

  const [formData, setFormData] = useState({
    name: "",
    type: "ORGANIZATION",
    aliases: "",
    external_id: "",
    registration_number: "",
    tax_id: "",
    country_code: "",
    address: "",
    category: "",
    subcategory: "",
    tags: "",
    criticality: 3,
    notes: "",
  });

  const [error, setError] = useState("");

  useEffect(() => {
    if (entity) {
      setFormData({
        name: entity.name || "",
        type: entity.type || "ORGANIZATION",
        aliases: entity.aliases?.join(", ") || "",
        external_id: entity.external_id || "",
        registration_number: entity.registration_number || "",
        tax_id: entity.tax_id || "",
        country_code: entity.country_code || "",
        address: entity.address || "",
        category: entity.category || "",
        subcategory: entity.subcategory || "",
        tags: entity.tags?.join(", ") || "",
        criticality: entity.criticality || 3,
        notes: entity.notes || "",
      });
    } else {
      setFormData({
        name: "",
        type: "ORGANIZATION",
        aliases: "",
        external_id: "",
        registration_number: "",
        tax_id: "",
        country_code: "",
        address: "",
        category: "",
        subcategory: "",
        tags: "",
        criticality: 3,
        notes: "",
      });
    }
    setError("");
  }, [entity, isOpen]);

  const mutation = useMutation({
    mutationFn: async (data: any) => {
      if (isEdit) {
        return entitiesApi.update(entity.id, data);
      }
      return entitiesApi.create(data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["entities"] });
      queryClient.invalidateQueries({ queryKey: ["entities-count"] });
      onClose();
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || "Failed to save risk object");
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    const payload = {
      ...formData,
      aliases: formData.aliases
        ? formData.aliases
            .split(",")
            .map((a) => a.trim())
            .filter(Boolean)
        : [],
      tags: formData.tags
        ? formData.tags
            .split(",")
            .map((t) => t.trim())
            .filter(Boolean)
        : [],
      country_code: formData.country_code || null,
      external_id: formData.external_id || null,
      registration_number: formData.registration_number || null,
      tax_id: formData.tax_id || null,
      address: formData.address || null,
      category: formData.category || null,
      subcategory: formData.subcategory || null,
      notes: formData.notes || null,
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
      [name]: name === "criticality" ? parseInt(value) : value,
    }));
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEdit ? "Edit Risk Object" : "Add New Risk Object"}
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
              Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="Risk object name"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Type <span className="text-red-500">*</span>
            </label>
            <select
              name="type"
              value={formData.type}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            >
              {entityTypes.map((type) => (
                <option key={type} value={type}>
                  {type}
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

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Country Code
            </label>
            <input
              type="text"
              name="country_code"
              value={formData.country_code}
              onChange={handleChange}
              maxLength={3}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="e.g., USA, GBR"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Category
            </label>
            <input
              type="text"
              name="category"
              value={formData.category}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="e.g., Technology, Finance"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Subcategory
            </label>
            <input
              type="text"
              name="subcategory"
              value={formData.subcategory}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="e.g., Software, Banking"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              External ID
            </label>
            <input
              type="text"
              name="external_id"
              value={formData.external_id}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="External system ID"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Registration Number
            </label>
            <input
              type="text"
              name="registration_number"
              value={formData.registration_number}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="Company registration"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tax ID
            </label>
            <input
              type="text"
              name="tax_id"
              value={formData.tax_id}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="Tax identification"
            />
          </div>

          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Address
            </label>
            <input
              type="text"
              name="address"
              value={formData.address}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="Full address"
            />
          </div>

          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Aliases (comma-separated)
            </label>
            <input
              type="text"
              name="aliases"
              value={formData.aliases}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="Alternative names, separated by commas"
            />
          </div>

          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tags (comma-separated)
            </label>
            <input
              type="text"
              name="tags"
              value={formData.tags}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="Tags, separated by commas"
            />
          </div>

          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Notes
            </label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              rows={3}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="Additional notes"
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
                ? "Update Risk Object"
                : "Create Risk Object"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
