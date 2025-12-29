import { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  DocumentTextIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  DocumentArrowDownIcon,
  PencilSquareIcon,
  DocumentDuplicateIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  BuildingLibraryIcon,
  ShieldCheckIcon,
  BanknotesIcon,
  ServerStackIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  XMarkIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline';
import {
  FRAMEWORKS,
  ALL_TEMPLATES,
  getTemplatesByFramework,
  getTemplateStats,
  DocumentTemplate,
  FrameworkInfo,
} from '../data/documentTemplates';
import { useLanguage } from '../contexts/LanguageContext';
import { russianComplianceApi, aiApi } from '../services/api';

interface Company {
  id: string;
  legal_name: string;
  inn: string;
}

const FRAMEWORK_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  '152-FZ': DocumentTextIcon,
  '187-FZ': ServerStackIcon,
  'GOST-57580': BanknotesIcon,
  'FSTEC-21': ShieldCheckIcon,
};

const FRAMEWORK_COLORS: Record<string, string> = {
  '152-FZ': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  '187-FZ': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
  'GOST-57580': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  'FSTEC-21': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
};

interface TemplateCustomization {
  template: DocumentTemplate;
  customName?: string;
  customFields: Record<string, string>;
}

export default function TemplateCatalog() {
  const { t, language } = useLanguage();
  const queryClient = useQueryClient();
  const [selectedFramework, setSelectedFramework] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showMandatoryOnly, setShowMandatoryOnly] = useState(false);
  const [showRegulatorOnly, setShowRegulatorOnly] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<DocumentTemplate | null>(null);
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());
  const [customization, setCustomization] = useState<TemplateCustomization | null>(null);
  const [selectedForGeneration, setSelectedForGeneration] = useState<Set<string>>(new Set());
  const [selectedCompanyId, setSelectedCompanyId] = useState<string | null>(null);

  // Fetch companies for selector
  const { data: companies = [] } = useQuery({
    queryKey: ["companies"],
    queryFn: () => russianComplianceApi.companies.list(),
  });

  // Document generation mutation
  const generateDocMutation = useMutation({
    mutationFn: async (templateIds: string[]) => {
      if (!selectedCompanyId) throw new Error("Please select a company first");
      const results = await Promise.all(
        templateIds.map(async (id) => {
          try {
            return await russianComplianceApi.smeTemplates.generate(id, { company_id: selectedCompanyId });
          } catch (error) {
            console.error(`Failed to generate template ${id}:`, error);
            return null;
          }
        })
      );
      return results.filter(Boolean);
    },
    onSuccess: (data) => {
      // Download generated documents
      data.forEach((response) => {
        const doc = response?.data;
        if (doc?.download_url) {
          window.open(doc.download_url, '_blank');
        }
      });
      setSelectedForGeneration(new Set());
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
  });

  // AI Document Generation
  const aiGenerateMutation = useMutation({
    mutationFn: async (documentType: string) => {
      if (!selectedCompanyId) throw new Error("Please select a company first");
      const company = (companies as { data?: Company[] })?.data?.find((c: Company) => c.id === selectedCompanyId);
      if (!company) throw new Error("Company not found");

      return aiApi.documents.generate({
        document_type: documentType,
        company_name: company.legal_name,
        company_inn: company.inn,
        framework: selectedFramework || "152-FZ",
      });
    },
    onSuccess: (response) => {
      const content = response?.data?.content;
      if (content) {
        // Create downloadable document
        const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ai_generated_document_${Date.now()}.txt`;
        a.click();
        URL.revokeObjectURL(url);
      }
    },
  });

  // Single template download
  const handleDownloadTemplate = async (templateId: string) => {
    if (!selectedCompanyId) {
      alert(language === 'ru' ? 'Пожалуйста, выберите компанию' : 'Please select a company first');
      return;
    }
    try {
      const response = await russianComplianceApi.smeTemplates.generate(templateId, {
        company_id: selectedCompanyId,
      });
      if (response?.data?.download_url) {
        window.open(response.data.download_url, '_blank');
      }
    } catch (error) {
      console.error('Failed to download template:', error);
      alert(language === 'ru' ? 'Ошибка при скачивании' : 'Download failed');
    }
  };

  const stats = getTemplateStats();

  // Filter templates
  const filteredTemplates = useMemo(() => {
    let templates = ALL_TEMPLATES;

    if (selectedFramework) {
      templates = templates.filter(t => t.framework === selectedFramework);
    }

    if (selectedCategory) {
      templates = templates.filter(t => t.category === selectedCategory);
    }

    if (showMandatoryOnly) {
      templates = templates.filter(t => t.mandatory);
    }

    if (showRegulatorOnly) {
      templates = templates.filter(t => t.regulatorSubmission);
    }

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      templates = templates.filter(t =>
        t.name.toLowerCase().includes(query) ||
        t.nameEn.toLowerCase().includes(query) ||
        t.code.toLowerCase().includes(query) ||
        t.description.toLowerCase().includes(query)
      );
    }

    return templates;
  }, [selectedFramework, selectedCategory, showMandatoryOnly, showRegulatorOnly, searchQuery]);

  // Group templates by category
  const templatesByCategory = useMemo(() => {
    const grouped: Record<string, DocumentTemplate[]> = {};
    filteredTemplates.forEach(template => {
      if (!grouped[template.category]) {
        grouped[template.category] = [];
      }
      grouped[template.category].push(template);
    });
    return grouped;
  }, [filteredTemplates]);

  // Get unique categories for current framework
  const availableCategories = useMemo(() => {
    const templates = selectedFramework
      ? getTemplatesByFramework(selectedFramework)
      : ALL_TEMPLATES;
    return [...new Set(templates.map(t => t.category))];
  }, [selectedFramework]);

  const toggleCategory = (category: string) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(category)) {
      newExpanded.delete(category);
    } else {
      newExpanded.add(category);
    }
    setExpandedCategories(newExpanded);
  };

  const toggleTemplateSelection = (templateId: string) => {
    const newSelected = new Set(selectedForGeneration);
    if (newSelected.has(templateId)) {
      newSelected.delete(templateId);
    } else {
      newSelected.add(templateId);
    }
    setSelectedForGeneration(newSelected);
  };

  const selectAllInCategory = (category: string) => {
    const newSelected = new Set(selectedForGeneration);
    const categoryTemplates = templatesByCategory[category] || [];
    const allSelected = categoryTemplates.every(t => newSelected.has(t.id));

    categoryTemplates.forEach(t => {
      if (allSelected) {
        newSelected.delete(t.id);
      } else {
        newSelected.add(t.id);
      }
    });
    setSelectedForGeneration(newSelected);
  };

  const handleGenerateDocuments = () => {
    if (selectedForGeneration.size === 0) return;
    if (!selectedCompanyId) {
      alert(language === 'ru' ? 'Пожалуйста, выберите компанию' : 'Please select a company first');
      return;
    }
    generateDocMutation.mutate(Array.from(selectedForGeneration));
  };

  const renderFrameworkCard = (framework: FrameworkInfo) => {
    const Icon = FRAMEWORK_ICONS[framework.code] || DocumentTextIcon;
    const stats = getTemplateStats().byFramework.find(f => f.code === framework.code);
    const isSelected = selectedFramework === framework.code;

    return (
      <button
        key={framework.code}
        onClick={() => setSelectedFramework(isSelected ? null : framework.code)}
        className={`p-4 rounded-lg border-2 transition-all text-left ${
          isSelected
            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
            : 'border-gray-200 dark:border-dark-600 hover:border-primary-300'
        }`}
      >
        <div className="flex items-start justify-between">
          <div className={`p-2 rounded-lg ${FRAMEWORK_COLORS[framework.code]}`}>
            <Icon className="h-6 w-6" />
          </div>
          {isSelected && (
            <CheckCircleIcon className="h-5 w-5 text-primary-500" />
          )}
        </div>
        <h3 className="mt-3 font-semibold text-gray-900 dark:text-gray-100">
          {framework.name}
        </h3>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
          {language === 'ru' ? framework.fullName : framework.nameEn}
        </p>
        <div className="mt-3 flex items-center gap-4 text-sm">
          <span className="text-gray-600 dark:text-gray-300">
            {stats?.count || 0} {language === 'ru' ? 'шаблонов' : 'templates'}
          </span>
          <span className="text-red-600 dark:text-red-400">
            {stats?.mandatory || 0} {language === 'ru' ? 'обязат.' : 'required'}
          </span>
        </div>
      </button>
    );
  };

  const renderTemplateRow = (template: DocumentTemplate) => {
    const isSelected = selectedForGeneration.has(template.id);

    return (
      <tr
        key={template.id}
        className={`hover:bg-gray-50 dark:hover:bg-dark-700 transition-colors ${
          isSelected ? 'bg-primary-50 dark:bg-primary-900/20' : ''
        }`}
      >
        <td className="px-4 py-3">
          <input
            type="checkbox"
            checked={isSelected}
            onChange={() => toggleTemplateSelection(template.id)}
            className="h-4 w-4 text-primary-600 rounded border-gray-300 dark:border-dark-500"
          />
        </td>
        <td className="px-4 py-3">
          <span className="font-mono text-sm text-gray-500 dark:text-gray-400">
            {template.code}
          </span>
        </td>
        <td className="px-4 py-3">
          <div>
            <p className="font-medium text-gray-900 dark:text-gray-100">
              {language === 'ru' ? template.name : template.nameEn}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5 line-clamp-1">
              {language === 'ru' ? template.description : template.descriptionEn}
            </p>
          </div>
        </td>
        <td className="px-4 py-3">
          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
            FRAMEWORK_COLORS[template.framework]
          }`}>
            {FRAMEWORKS.find(f => f.code === template.framework)?.name}
          </span>
        </td>
        <td className="px-4 py-3 text-sm text-gray-500 dark:text-gray-400">
          {template.pages} {language === 'ru' ? 'стр.' : 'pages'}
        </td>
        <td className="px-4 py-3">
          <div className="flex items-center gap-2">
            {template.mandatory && (
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">
                {language === 'ru' ? 'Обязат.' : 'Required'}
              </span>
            )}
            {template.regulatorSubmission && (
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
                {language === 'ru' ? 'Подача' : 'Submit'}
              </span>
            )}
            {template.autoFill && (
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                {language === 'ru' ? 'Авто' : 'Auto'}
              </span>
            )}
          </div>
        </td>
        <td className="px-4 py-3">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setSelectedTemplate(template)}
              className="p-1.5 text-gray-400 hover:text-primary-600 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-600"
              title={language === 'ru' ? 'Просмотр' : 'View'}
            >
              <DocumentTextIcon className="h-5 w-5" />
            </button>
            <button
              onClick={() => setCustomization({ template, customFields: {} })}
              className="p-1.5 text-gray-400 hover:text-primary-600 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-600"
              title={language === 'ru' ? 'Настроить' : 'Customize'}
            >
              <PencilSquareIcon className="h-5 w-5" />
            </button>
            <button
              className="p-1.5 text-gray-400 hover:text-primary-600 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-600"
              title={language === 'ru' ? 'Скачать' : 'Download'}
            >
              <DocumentArrowDownIcon className="h-5 w-5" />
            </button>
          </div>
        </td>
      </tr>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            {language === 'ru' ? 'Каталог шаблонов' : 'Template Catalog'}
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {language === 'ru'
              ? `${stats.total} шаблонов для ${FRAMEWORKS.length} нормативных актов`
              : `${stats.total} templates for ${FRAMEWORKS.length} regulatory frameworks`}
          </p>
        </div>
        <div className="flex items-center gap-3">
          {/* Company Selector */}
          <select
            value={selectedCompanyId || ""}
            onChange={(e) => setSelectedCompanyId(e.target.value || null)}
            className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
          >
            <option value="">{language === 'ru' ? 'Выберите компанию' : 'Select Company'}</option>
            {(companies as Company[]).map((company) => (
              <option key={company.id} value={company.id}>
                {company.legal_name} ({company.inn})
              </option>
            ))}
          </select>
          {selectedForGeneration.size > 0 && (
            <button
              onClick={handleGenerateDocuments}
              disabled={generateDocMutation.isPending || !selectedCompanyId}
              className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {generateDocMutation.isPending ? (
                <>
                  <ArrowPathIcon className="h-5 w-5 animate-spin" />
                  {language === 'ru' ? 'Генерация...' : 'Generating...'}
                </>
              ) : (
                <>
                  <DocumentDuplicateIcon className="h-5 w-5" />
                  {language === 'ru'
                    ? `Генерировать (${selectedForGeneration.size})`
                    : `Generate (${selectedForGeneration.size})`}
                </>
              )}
            </button>
          )}
          {/* AI Generate Button */}
          <button
            onClick={() => aiGenerateMutation.mutate('policy')}
            disabled={aiGenerateMutation.isPending || !selectedCompanyId}
            className="btn-secondary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed bg-gradient-to-r from-purple-500 to-indigo-600 text-white hover:from-purple-600 hover:to-indigo-700"
          >
            {aiGenerateMutation.isPending ? (
              <>
                <ArrowPathIcon className="h-5 w-5 animate-spin" />
                {language === 'ru' ? 'AI генерация...' : 'AI Generating...'}
              </>
            ) : (
              <>
                <span className="text-lg">✨</span>
                {language === 'ru' ? 'AI Генерация' : 'AI Generate'}
              </>
            )}
          </button>
        </div>
      </div>

      {/* Framework Selection */}
      <div>
        <h2 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
          {language === 'ru' ? 'Нормативные акты' : 'Regulatory Frameworks'}
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {FRAMEWORKS.map(renderFrameworkCard)}
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white dark:bg-dark-800 rounded-lg border border-gray-200 dark:border-dark-600 p-4">
        <div className="flex flex-wrap items-center gap-4">
          {/* Search */}
          <div className="relative flex-1 min-w-[200px]">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={language === 'ru' ? 'Поиск шаблонов...' : 'Search templates...'}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-dark-500 rounded-lg bg-white dark:bg-dark-700 text-gray-900 dark:text-gray-100"
            />
          </div>

          {/* Category Filter */}
          <select
            value={selectedCategory || ''}
            onChange={(e) => setSelectedCategory(e.target.value || null)}
            className="px-4 py-2 border border-gray-300 dark:border-dark-500 rounded-lg bg-white dark:bg-dark-700 text-gray-900 dark:text-gray-100"
          >
            <option value="">{language === 'ru' ? 'Все категории' : 'All categories'}</option>
            {availableCategories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>

          {/* Toggle Filters */}
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={showMandatoryOnly}
                onChange={(e) => setShowMandatoryOnly(e.target.checked)}
                className="h-4 w-4 text-primary-600 rounded border-gray-300 dark:border-dark-500"
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                {language === 'ru' ? 'Только обязательные' : 'Required only'}
              </span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={showRegulatorOnly}
                onChange={(e) => setShowRegulatorOnly(e.target.checked)}
                className="h-4 w-4 text-primary-600 rounded border-gray-300 dark:border-dark-500"
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                {language === 'ru' ? 'Для подачи в регулятор' : 'Regulator submission'}
              </span>
            </label>
          </div>
        </div>
      </div>

      {/* Templates Table */}
      <div className="bg-white dark:bg-dark-800 rounded-lg border border-gray-200 dark:border-dark-600 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-dark-600">
            <thead className="bg-gray-50 dark:bg-dark-700">
              <tr>
                <th className="px-4 py-3 text-left">
                  <input
                    type="checkbox"
                    checked={filteredTemplates.length > 0 && filteredTemplates.every(t => selectedForGeneration.has(t.id))}
                    onChange={() => {
                      const allSelected = filteredTemplates.every(t => selectedForGeneration.has(t.id));
                      const newSelected = new Set(selectedForGeneration);
                      filteredTemplates.forEach(t => {
                        if (allSelected) {
                          newSelected.delete(t.id);
                        } else {
                          newSelected.add(t.id);
                        }
                      });
                      setSelectedForGeneration(newSelected);
                    }}
                    className="h-4 w-4 text-primary-600 rounded border-gray-300 dark:border-dark-500"
                  />
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  {language === 'ru' ? 'Код' : 'Code'}
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  {language === 'ru' ? 'Название' : 'Name'}
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  {language === 'ru' ? 'Фреймворк' : 'Framework'}
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  {language === 'ru' ? 'Объем' : 'Size'}
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  {language === 'ru' ? 'Тип' : 'Type'}
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  {language === 'ru' ? 'Действия' : 'Actions'}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-dark-600">
              {filteredTemplates.map(renderTemplateRow)}
            </tbody>
          </table>
        </div>

        {filteredTemplates.length === 0 && (
          <div className="text-center py-12">
            <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">
              {language === 'ru' ? 'Шаблоны не найдены' : 'No templates found'}
            </h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {language === 'ru'
                ? 'Попробуйте изменить параметры фильтрации'
                : 'Try adjusting your filter criteria'}
            </p>
          </div>
        )}
      </div>

      {/* Template Detail Modal */}
      {selectedTemplate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white dark:bg-dark-800 rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white dark:bg-dark-800 border-b border-gray-200 dark:border-dark-600 p-4 flex items-center justify-between">
              <div>
                <span className="text-sm font-mono text-gray-500 dark:text-gray-400">
                  {selectedTemplate.code}
                </span>
                <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                  {language === 'ru' ? selectedTemplate.name : selectedTemplate.nameEn}
                </h2>
              </div>
              <button
                onClick={() => setSelectedTemplate(null)}
                className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-700"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>

            <div className="p-6 space-y-6">
              <div>
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                  {language === 'ru' ? 'Описание' : 'Description'}
                </h3>
                <p className="text-gray-900 dark:text-gray-100">
                  {language === 'ru' ? selectedTemplate.description : selectedTemplate.descriptionEn}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                    {language === 'ru' ? 'Нормативный акт' : 'Framework'}
                  </h3>
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                    FRAMEWORK_COLORS[selectedTemplate.framework]
                  }`}>
                    {FRAMEWORKS.find(f => f.code === selectedTemplate.framework)?.name}
                  </span>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                    {language === 'ru' ? 'Категория' : 'Category'}
                  </h3>
                  <span className="text-gray-900 dark:text-gray-100">
                    {selectedTemplate.category}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                    {language === 'ru' ? 'Объем' : 'Pages'}
                  </h3>
                  <span className="text-gray-900 dark:text-gray-100">
                    {selectedTemplate.pages} {language === 'ru' ? 'страниц' : 'pages'}
                  </span>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                    {language === 'ru' ? 'Формат' : 'Format'}
                  </h3>
                  <span className="text-gray-900 dark:text-gray-100 uppercase">
                    {selectedTemplate.format}
                  </span>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                    {language === 'ru' ? 'Авто-заполнение' : 'Auto-fill'}
                  </h3>
                  <span className={selectedTemplate.autoFill ? 'text-green-600' : 'text-gray-500'}>
                    {selectedTemplate.autoFill
                      ? (language === 'ru' ? 'Да' : 'Yes')
                      : (language === 'ru' ? 'Нет' : 'No')}
                  </span>
                </div>
              </div>

              {selectedTemplate.variables.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                    {language === 'ru' ? 'Переменные для заполнения' : 'Variables'}
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedTemplate.variables.map(v => (
                      <span
                        key={v}
                        className="px-2 py-1 bg-gray-100 dark:bg-dark-700 rounded text-sm font-mono text-gray-700 dark:text-gray-300"
                      >
                        {`{{${v}}}`}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex items-center gap-3">
                {selectedTemplate.mandatory && (
                  <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">
                    <ExclamationTriangleIcon className="h-4 w-4" />
                    {language === 'ru' ? 'Обязательный документ' : 'Mandatory document'}
                  </span>
                )}
                {selectedTemplate.regulatorSubmission && (
                  <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
                    <BuildingLibraryIcon className="h-4 w-4" />
                    {language === 'ru' ? 'Подача в регулятор' : 'Regulator submission'}
                  </span>
                )}
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-dark-600">
                <button
                  onClick={() => {
                    setCustomization({ template: selectedTemplate, customFields: {} });
                    setSelectedTemplate(null);
                  }}
                  className="btn-secondary flex items-center gap-2"
                >
                  <PencilSquareIcon className="h-5 w-5" />
                  {language === 'ru' ? 'Настроить' : 'Customize'}
                </button>
                <button className="btn-primary flex items-center gap-2">
                  <DocumentArrowDownIcon className="h-5 w-5" />
                  {language === 'ru' ? 'Скачать шаблон' : 'Download Template'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Template Customization Modal */}
      {customization && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white dark:bg-dark-800 rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white dark:bg-dark-800 border-b border-gray-200 dark:border-dark-600 p-4 flex items-center justify-between">
              <div>
                <span className="text-sm font-mono text-gray-500 dark:text-gray-400">
                  {customization.template.code}
                </span>
                <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                  {language === 'ru' ? 'Настройка шаблона' : 'Customize Template'}
                </h2>
              </div>
              <button
                onClick={() => setCustomization(null)}
                className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-700"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>

            <div className="p-6 space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {language === 'ru' ? 'Название документа' : 'Document Name'}
                </label>
                <input
                  type="text"
                  value={customization.customName || ''}
                  onChange={(e) => setCustomization({
                    ...customization,
                    customName: e.target.value,
                  })}
                  placeholder={language === 'ru' ? customization.template.name : customization.template.nameEn}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-dark-500 rounded-lg bg-white dark:bg-dark-700 text-gray-900 dark:text-gray-100"
                />
              </div>

              {customization.template.variables.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-4">
                    {language === 'ru' ? 'Значения переменных' : 'Variable Values'}
                  </h3>
                  <div className="space-y-4">
                    {customization.template.variables.map(variable => (
                      <div key={variable}>
                        <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">
                          {variable}
                        </label>
                        <input
                          type="text"
                          value={customization.customFields[variable] || ''}
                          onChange={(e) => setCustomization({
                            ...customization,
                            customFields: {
                              ...customization.customFields,
                              [variable]: e.target.value,
                            },
                          })}
                          placeholder={`{{${variable}}}`}
                          className="w-full px-4 py-2 border border-gray-300 dark:border-dark-500 rounded-lg bg-white dark:bg-dark-700 text-gray-900 dark:text-gray-100"
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-dark-600">
                <button
                  onClick={() => setCustomization(null)}
                  className="btn-secondary"
                >
                  {language === 'ru' ? 'Отмена' : 'Cancel'}
                </button>
                <button className="btn-primary flex items-center gap-2">
                  <DocumentDuplicateIcon className="h-5 w-5" />
                  {language === 'ru' ? 'Создать документ' : 'Generate Document'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
