import React, { useState, useMemo } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';
import {
  MagnifyingGlassIcon,
  FunnelIcon,
  DocumentTextIcon,
  BuildingOfficeIcon,
  UserGroupIcon,
  DocumentDuplicateIcon,
  BanknotesIcon,
  CalculatorIcon,
  ScaleIcon,
  BuildingStorefrontIcon,
  HomeModernIcon,
  BuildingLibraryIcon,
  ClipboardDocumentListIcon,
  IdentificationIcon,
  ShieldExclamationIcon,
  TruckIcon,
  CheckBadgeIcon,
  ExclamationTriangleIcon,
  XMarkIcon,
  ArrowDownTrayIcon,
  ShareIcon,
  ArchiveBoxIcon,
  DocumentArrowDownIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';
import { russianComplianceApi } from '../services/api';

// Template categories
type TemplateCategory =
  | 'corporate'
  | 'hr'
  | 'contracts'
  | 'financial'
  | 'tax'
  | 'legal'
  | 'industry'
  | 'real_estate'
  | 'banking'
  | 'gov_tenders'
  | 'licenses'
  | 'environmental'
  | 'vehicles'
  | 'quality'
  | 'crisis'
  | 'grc_compliance'
  | 'specialized';

interface CategoryInfo {
  id: TemplateCategory;
  name: string;
  nameEn: string;
  icon: React.ElementType;
  color: string;
  bgColor: string;
}

interface ApiTemplate {
  id: string;
  name: string;
  category: string;
  description: string | null;
  tags: string[];
  regulatory_refs: string[];
}

interface ApiCategory {
  id: string;
  name: string;
  name_en: string | null;
  template_count: number;
}

const CATEGORY_ICONS: Record<string, { icon: React.ElementType; color: string; bgColor: string }> = {
  corporate: { icon: BuildingOfficeIcon, color: 'text-blue-600', bgColor: 'bg-blue-50' },
  hr: { icon: UserGroupIcon, color: 'text-green-600', bgColor: 'bg-green-50' },
  contracts: { icon: DocumentDuplicateIcon, color: 'text-purple-600', bgColor: 'bg-purple-50' },
  financial: { icon: BanknotesIcon, color: 'text-emerald-600', bgColor: 'bg-emerald-50' },
  tax: { icon: CalculatorIcon, color: 'text-orange-600', bgColor: 'bg-orange-50' },
  legal: { icon: ScaleIcon, color: 'text-red-600', bgColor: 'bg-red-50' },
  industry: { icon: BuildingStorefrontIcon, color: 'text-cyan-600', bgColor: 'bg-cyan-50' },
  real_estate: { icon: HomeModernIcon, color: 'text-amber-600', bgColor: 'bg-amber-50' },
  banking: { icon: BuildingLibraryIcon, color: 'text-indigo-600', bgColor: 'bg-indigo-50' },
  gov_tenders: { icon: ClipboardDocumentListIcon, color: 'text-teal-600', bgColor: 'bg-teal-50' },
  licenses: { icon: IdentificationIcon, color: 'text-pink-600', bgColor: 'bg-pink-50' },
  environmental: { icon: ShieldExclamationIcon, color: 'text-lime-600', bgColor: 'bg-lime-50' },
  vehicles: { icon: TruckIcon, color: 'text-slate-600', bgColor: 'bg-slate-50' },
  quality: { icon: CheckBadgeIcon, color: 'text-violet-600', bgColor: 'bg-violet-50' },
  crisis: { icon: ExclamationTriangleIcon, color: 'text-rose-600', bgColor: 'bg-rose-50' },
  grc_compliance: { icon: DocumentTextIcon, color: 'text-gray-600', bgColor: 'bg-gray-50' },
  specialized: { icon: SparklesIcon, color: 'text-fuchsia-600', bgColor: 'bg-fuchsia-50' },
  general: { icon: DocumentTextIcon, color: 'text-gray-600', bgColor: 'bg-gray-50' },
};

const SMETemplates: React.FC = () => {
  const [searchParams] = useSearchParams();
  const initialTemplate = searchParams.get('template');
  const { language } = useLanguage();

  // Bilingual translations
  const t = {
    title: language === 'ru' ? 'Шаблоны документов для бизнеса' : 'Business Document Templates',
    subtitle: language === 'ru' ? '+ шаблонов для всех этапов развития компании' : '+ templates for all company lifecycle stages',
    found: language === 'ru' ? 'Найдено' : 'Found',
    searchPlaceholder: language === 'ru' ? 'Поиск шаблонов...' : 'Search templates...',
    categories: language === 'ru' ? 'Категории' : 'Categories',
    all: language === 'ru' ? 'Все' : 'All',
    allTemplates: language === 'ru' ? 'Все шаблоны' : 'All templates',
    loadingCategories: language === 'ru' ? 'Загрузка категорий...' : 'Loading categories...',
    loadingTemplates: language === 'ru' ? 'Загрузка шаблонов...' : 'Loading templates...',
    noTemplates: language === 'ru' ? 'Шаблоны не найдены' : 'No templates found',
    tryDifferent: language === 'ru' ? 'Попробуйте изменить критерии поиска' : 'Try different search criteria',
    category: language === 'ru' ? 'Категория' : 'Category',
    description: language === 'ru' ? 'Описание' : 'Description',
    noDescription: language === 'ru' ? 'Нет описания' : 'No description',
    regulatoryRefs: language === 'ru' ? 'Нормативные ссылки' : 'Regulatory references',
    tags: language === 'ru' ? 'Теги' : 'Tags',
    generatedDoc: language === 'ru' ? 'Сгенерированный документ' : 'Generated document',
    downloadDoc: language === 'ru' ? 'Скачать документ' : 'Download document',
    back: language === 'ru' ? 'Назад' : 'Back',
    createDoc: language === 'ru' ? 'Создать документ' : 'Create document',
    generating: language === 'ru' ? 'Генерация...' : 'Generating...',
    downloadTemplate: language === 'ru' ? 'Скачать шаблон' : 'Download template',
    share: language === 'ru' ? 'Поделиться' : 'Share',
    archive: language === 'ru' ? 'В архив' : 'Archive',
  };

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<ApiTemplate | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [generatedContent, setGeneratedContent] = useState<string | null>(null);

  // Fetch templates from API
  const { data: templates = [], isLoading: templatesLoading } = useQuery({
    queryKey: ['sme-templates', selectedCategory],
    queryFn: async () => {
      const response = await russianComplianceApi.smeTemplates.list({
        category: selectedCategory || undefined,
      });
      return response.data as ApiTemplate[];
    },
  });

  // Fetch categories from API
  const { data: categories = [], isLoading: categoriesLoading } = useQuery({
    queryKey: ['sme-template-categories'],
    queryFn: async () => {
      const response = await russianComplianceApi.smeTemplates.getCategories();
      return response.data as ApiCategory[];
    },
  });

  // Fetch statistics
  const { data: statistics } = useQuery({
    queryKey: ['sme-template-statistics'],
    queryFn: async () => {
      const response = await russianComplianceApi.smeTemplates.getStatistics();
      return response.data as { total_templates: number; categories: number };
    },
  });

  // Generate document mutation
  const generateMutation = useMutation({
    mutationFn: async (templateId: string) => {
      const response = await russianComplianceApi.smeTemplates.generate(templateId, {});
      return response.data as { content: string; template_name: string };
    },
    onSuccess: (data) => {
      setGeneratedContent(data.content);
    },
  });

  // Filter templates by search
  const filteredTemplates = useMemo(() => {
    if (!searchQuery.trim()) return templates;

    const query = searchQuery.toLowerCase();
    return templates.filter(t =>
      t.name.toLowerCase().includes(query) ||
      t.id.toLowerCase().includes(query) ||
      (t.description && t.description.toLowerCase().includes(query))
    );
  }, [templates, searchQuery]);

  // Get category info
  const getCategoryInfo = (categoryId: string) => {
    return CATEGORY_ICONS[categoryId] || CATEGORY_ICONS.general;
  };

  // Total template count
  const totalTemplates = statistics?.total_templates || categories.reduce((sum, c) => sum + c.template_count, 0);

  const handleGenerateDocument = () => {
    if (selectedTemplate) {
      generateMutation.mutate(selectedTemplate.id);
    }
  };

  const handleDownloadDocument = () => {
    if (generatedContent && selectedTemplate) {
      const blob = new Blob([generatedContent], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${selectedTemplate.name}.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {t.title}
              </h1>
              <p className="mt-1 text-sm text-gray-500">
                {totalTemplates}{t.subtitle}
              </p>
            </div>
            <div className="mt-4 sm:mt-0 flex items-center space-x-3">
              <span className="text-sm text-gray-500">
                {t.found}: {filteredTemplates.length}
              </span>
            </div>
          </div>

          {/* Search */}
          <div className="mt-4 flex gap-4">
            <div className="flex-1 relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder={t.searchPlaceholder}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`px-4 py-2 border rounded-lg flex items-center ${
                showFilters ? 'bg-blue-50 border-blue-300 text-blue-700' : 'border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              <FunnelIcon className="h-5 w-5 mr-2" />
              {t.categories}
            </button>
          </div>
        </div>
      </div>

      {/* Category Filters */}
      {showFilters && (
        <div className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            {categoriesLoading ? (
              <div className="text-center text-gray-500">{t.loadingCategories}</div>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2">
                <button
                  onClick={() => setSelectedCategory(null)}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    selectedCategory === null
                      ? 'bg-gray-900 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {t.all} ({totalTemplates})
                </button>
                {categories.map((category) => {
                  const info = getCategoryInfo(category.id);
                  const Icon = info.icon;
                  const isSelected = selectedCategory === category.id;
                  return (
                    <button
                      key={category.id}
                      onClick={() => setSelectedCategory(isSelected ? null : category.id)}
                      className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center ${
                        isSelected
                          ? `${info.bgColor} ${info.color}`
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      <Icon className="h-4 w-4 mr-1" />
                      <span className="truncate">{category.name}</span>
                      <span className="ml-1 text-xs opacity-70">({category.template_count})</span>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar - Categories */}
          <div className="lg:col-span-1 hidden lg:block">
            <div className="bg-white rounded-lg border border-gray-200 sticky top-8">
              <div className="px-4 py-3 border-b border-gray-200">
                <h3 className="font-medium text-gray-900">{t.categories}</h3>
              </div>
              <div className="p-2">
                <button
                  onClick={() => setSelectedCategory(null)}
                  className={`w-full px-3 py-2 rounded-lg text-left text-sm transition-colors ${
                    selectedCategory === null
                      ? 'bg-gray-100 font-medium'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  {t.allTemplates}
                  <span className="float-right text-gray-500">{totalTemplates}</span>
                </button>
                {categories.map((category) => {
                  const info = getCategoryInfo(category.id);
                  const Icon = info.icon;
                  const isSelected = selectedCategory === category.id;
                  return (
                    <button
                      key={category.id}
                      onClick={() => setSelectedCategory(isSelected ? null : category.id)}
                      className={`w-full px-3 py-2 rounded-lg text-left text-sm transition-colors flex items-center ${
                        isSelected ? `${info.bgColor} ${info.color}` : 'hover:bg-gray-50'
                      }`}
                    >
                      <Icon className={`h-4 w-4 mr-2 ${isSelected ? info.color : 'text-gray-400'}`} />
                      <span className="truncate flex-1">{category.name}</span>
                      <span className={`text-xs ${isSelected ? info.color : 'text-gray-500'}`}>
                        {category.template_count}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Template Grid */}
          <div className="lg:col-span-3">
            {templatesLoading ? (
              <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
                <div className="animate-spin h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full mx-auto"></div>
                <p className="mt-4 text-gray-500">{t.loadingTemplates}</p>
              </div>
            ) : filteredTemplates.length === 0 ? (
              <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
                <DocumentTextIcon className="h-12 w-12 text-gray-400 mx-auto" />
                <h3 className="mt-4 text-lg font-medium text-gray-900">
                  {t.noTemplates}
                </h3>
                <p className="mt-2 text-sm text-gray-500">
                  {t.tryDifferent}
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {filteredTemplates.map((template) => {
                  const categoryInfo = getCategoryInfo(template.category);
                  return (
                    <div
                      key={template.id}
                      onClick={() => setSelectedTemplate(template)}
                      className="bg-white rounded-lg border border-gray-200 p-4 hover:border-gray-300 hover:shadow-sm cursor-pointer transition-all"
                    >
                      <div className="flex items-start">
                        <div className={`p-2 rounded-lg ${categoryInfo.bgColor}`}>
                          <DocumentTextIcon className={`h-5 w-5 ${categoryInfo.color}`} />
                        </div>
                        <div className="ml-3 flex-1 min-w-0">
                          <h4 className="font-medium text-gray-900 truncate">
                            {template.name}
                          </h4>
                          <p className="mt-1 text-sm text-gray-500 line-clamp-2">
                            {template.description || `${t.category}: ${template.category}`}
                          </p>
                          <div className="mt-2 flex flex-wrap gap-1">
                            <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${categoryInfo.bgColor} ${categoryInfo.color}`}>
                              {template.category}
                            </span>
                            {template.regulatory_refs?.slice(0, 2).map((ref) => (
                              <span key={ref} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600">
                                {ref}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Template Detail Modal */}
      {selectedTemplate && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-gray-200 flex items-start justify-between">
              <div className="flex items-center">
                <div className={`p-2 rounded-lg ${getCategoryInfo(selectedTemplate.category).bgColor}`}>
                  <DocumentTextIcon className={`h-6 w-6 ${getCategoryInfo(selectedTemplate.category).color}`} />
                </div>
                <div className="ml-3">
                  <h2 className="text-xl font-bold text-gray-900">{selectedTemplate.name}</h2>
                  <p className="text-sm text-gray-500">{selectedTemplate.category}</p>
                </div>
              </div>
              <button
                onClick={() => {
                  setSelectedTemplate(null);
                  setGeneratedContent(null);
                }}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <XMarkIcon className="h-5 w-5 text-gray-500" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6">
              {generatedContent ? (
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-2">{t.generatedDoc}</h3>
                  <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                    <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono">
                      {generatedContent}
                    </pre>
                  </div>
                  <div className="mt-4 flex gap-3">
                    <button
                      onClick={handleDownloadDocument}
                      className="flex-1 flex items-center justify-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                    >
                      <DocumentArrowDownIcon className="h-5 w-5 mr-2" />
                      {t.downloadDoc}
                    </button>
                    <button
                      onClick={() => setGeneratedContent(null)}
                      className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      {t.back}
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <div className="mb-6">
                    <h3 className="text-sm font-medium text-gray-500 mb-1">{t.description}</h3>
                    <p className="text-gray-900">{selectedTemplate.description || t.noDescription}</p>
                  </div>

                  {selectedTemplate.regulatory_refs && selectedTemplate.regulatory_refs.length > 0 && (
                    <div className="mb-6">
                      <h3 className="text-sm font-medium text-gray-500 mb-2">{t.regulatoryRefs}</h3>
                      <div className="flex flex-wrap gap-2">
                        {selectedTemplate.regulatory_refs.map((ref) => (
                          <span key={ref} className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-50 text-blue-700">
                            {ref}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {selectedTemplate.tags && selectedTemplate.tags.length > 0 && (
                    <div className="mb-6">
                      <h3 className="text-sm font-medium text-gray-500 mb-2">{t.tags}</h3>
                      <div className="flex flex-wrap gap-2">
                        {selectedTemplate.tags.map((tag) => (
                          <span key={tag} className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-gray-100 text-gray-700">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex flex-col sm:flex-row gap-3 pt-4 border-t border-gray-200">
                    <button
                      onClick={handleGenerateDocument}
                      disabled={generateMutation.isPending}
                      className="flex-1 flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                    >
                      {generateMutation.isPending ? (
                        <>
                          <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full mr-2"></div>
                          {t.generating}
                        </>
                      ) : (
                        <>
                          <DocumentTextIcon className="h-5 w-5 mr-2" />
                          {t.createDoc}
                        </>
                      )}
                    </button>
                    <button className="flex items-center justify-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                      <ArrowDownTrayIcon className="h-5 w-5 mr-2 text-gray-500" />
                      {t.downloadTemplate}
                    </button>
                    <button className="flex items-center justify-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                      <ShareIcon className="h-5 w-5 mr-2 text-gray-500" />
                      {t.share}
                    </button>
                    <button className="flex items-center justify-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                      <ArchiveBoxIcon className="h-5 w-5 mr-2 text-gray-500" />
                      {t.archive}
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SMETemplates;
