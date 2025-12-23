import { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import Modal from '../common/Modal'
import { constraintsApi } from '../../services/api'

interface ConstraintFormProps {
  isOpen: boolean
  onClose: () => void
  constraint?: any
}

const constraintTypes = ['POLICY', 'REGULATION', 'COMPLIANCE', 'CONTRACTUAL', 'OPERATIONAL', 'FINANCIAL', 'SECURITY']
const severityLevels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']

export default function ConstraintForm({ isOpen, onClose, constraint }: ConstraintFormProps) {
  const queryClient = useQueryClient()
  const isEdit = !!constraint

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    type: 'REGULATION',
    severity: 'MEDIUM',
    reference_code: '',
    source_document: '',
    external_url: '',
    applies_to_entity_types: '',
    applies_to_countries: '',
    applies_to_categories: '',
    effective_date: '',
    expiry_date: '',
    review_date: '',
    risk_weight: 1.0,
    is_mandatory: true,
    tags: '',
  })

  const [error, setError] = useState('')

  useEffect(() => {
    if (constraint) {
      setFormData({
        name: constraint.name || '',
        description: constraint.description || '',
        type: constraint.type || 'REGULATION',
        severity: constraint.severity || 'MEDIUM',
        reference_code: constraint.reference_code || '',
        source_document: constraint.source_document || '',
        external_url: constraint.external_url || '',
        applies_to_entity_types: constraint.applies_to_entity_types?.join(', ') || '',
        applies_to_countries: constraint.applies_to_countries?.join(', ') || '',
        applies_to_categories: constraint.applies_to_categories?.join(', ') || '',
        effective_date: constraint.effective_date?.split('T')[0] || '',
        expiry_date: constraint.expiry_date?.split('T')[0] || '',
        review_date: constraint.review_date?.split('T')[0] || '',
        risk_weight: constraint.risk_weight || 1.0,
        is_mandatory: constraint.is_mandatory ?? true,
        tags: constraint.tags?.join(', ') || '',
      })
    } else {
      setFormData({
        name: '',
        description: '',
        type: 'REGULATION',
        severity: 'MEDIUM',
        reference_code: '',
        source_document: '',
        external_url: '',
        applies_to_entity_types: '',
        applies_to_countries: '',
        applies_to_categories: '',
        effective_date: '',
        expiry_date: '',
        review_date: '',
        risk_weight: 1.0,
        is_mandatory: true,
        tags: '',
      })
    }
    setError('')
  }, [constraint, isOpen])

  const mutation = useMutation({
    mutationFn: async (data: any) => {
      if (isEdit) {
        return constraintsApi.update(constraint.id, data)
      }
      return constraintsApi.create(data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['constraints'] })
      queryClient.invalidateQueries({ queryKey: ['constraints-summary'] })
      onClose()
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to save constraint')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    const payload = {
      ...formData,
      applies_to_entity_types: formData.applies_to_entity_types ? formData.applies_to_entity_types.split(',').map(s => s.trim()).filter(Boolean) : [],
      applies_to_countries: formData.applies_to_countries ? formData.applies_to_countries.split(',').map(s => s.trim()).filter(Boolean) : [],
      applies_to_categories: formData.applies_to_categories ? formData.applies_to_categories.split(',').map(s => s.trim()).filter(Boolean) : [],
      tags: formData.tags ? formData.tags.split(',').map(t => t.trim()).filter(Boolean) : [],
      effective_date: formData.effective_date || null,
      expiry_date: formData.expiry_date || null,
      review_date: formData.review_date || null,
      description: formData.description || null,
      reference_code: formData.reference_code || null,
      source_document: formData.source_document || null,
      external_url: formData.external_url || null,
    }

    mutation.mutate(payload)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked :
              name === 'risk_weight' ? parseFloat(value) : value,
    }))
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={isEdit ? 'Edit Constraint' : 'Add New Constraint'} size="lg">
      <form onSubmit={handleSubmit} className="space-y-4 max-h-[70vh] overflow-y-auto">
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
              placeholder="Constraint name"
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
              {constraintTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Severity
            </label>
            <select
              name="severity"
              value={formData.severity}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            >
              {severityLevels.map(level => (
                <option key={level} value={level}>{level}</option>
              ))}
            </select>
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
              placeholder="Describe the constraint"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Reference Code
            </label>
            <input
              type="text"
              name="reference_code"
              value={formData.reference_code}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="e.g., OFAC-SDN-001"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Risk Weight (0-10)
            </label>
            <input
              type="number"
              name="risk_weight"
              value={formData.risk_weight}
              onChange={handleChange}
              min="0"
              max="10"
              step="0.1"
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Source Document
            </label>
            <input
              type="text"
              name="source_document"
              value={formData.source_document}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="Document reference"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              External URL
            </label>
            <input
              type="url"
              name="external_url"
              value={formData.external_url}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="https://..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Effective Date
            </label>
            <input
              type="date"
              name="effective_date"
              value={formData.effective_date}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Expiry Date
            </label>
            <input
              type="date"
              name="expiry_date"
              value={formData.expiry_date}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Review Date
            </label>
            <input
              type="date"
              name="review_date"
              value={formData.review_date}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            />
          </div>

          <div className="flex items-center pt-6">
            <input
              type="checkbox"
              name="is_mandatory"
              checked={formData.is_mandatory}
              onChange={handleChange}
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label className="ml-2 block text-sm text-gray-700">
              Mandatory constraint
            </label>
          </div>

          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Applies to Entity Types (comma-separated)
            </label>
            <input
              type="text"
              name="applies_to_entity_types"
              value={formData.applies_to_entity_types}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="ORGANIZATION, INDIVIDUAL (leave empty for all)"
            />
          </div>

          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Applies to Countries (comma-separated)
            </label>
            <input
              type="text"
              name="applies_to_countries"
              value={formData.applies_to_countries}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              placeholder="USA, GBR (leave empty for all)"
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
              placeholder="sanctions, compliance, etc."
            />
          </div>
        </div>

        <div className="flex justify-end space-x-3 pt-4 border-t">
          <button type="button" onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button type="submit" disabled={mutation.isPending} className="btn-primary">
            {mutation.isPending ? 'Saving...' : isEdit ? 'Update Constraint' : 'Create Constraint'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
