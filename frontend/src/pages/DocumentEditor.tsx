import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ArrowLeftIcon,
  DocumentTextIcon,
  ArrowDownTrayIcon,
  PrinterIcon,
  CheckIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  PencilIcon,
  EyeIcon,
  DocumentDuplicateIcon,
  TrashIcon,
  ArrowPathIcon,
} from "@heroicons/react/24/outline";
import { russianComplianceApi } from "../services/api";

interface DocumentVersion {
  id: string;
  version: number;
  content: string;
  changedBy: string;
  changedAt: string;
  comment: string;
}

export default function DocumentEditor() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const editorRef = useRef<HTMLDivElement>(null);

  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState("");
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [showVersions, setShowVersions] = useState(false);
  const [selectedVersion, setSelectedVersion] = useState<DocumentVersion | null>(null);

  // Fetch document
  const { data: document, isLoading } = useQuery({
    queryKey: ["document", id],
    queryFn: async () => {
      // In production this would call the API
      // For now, return mock data
      return {
        id: id,
        title: "Политика обработки персональных данных",
        titleEn: "Personal Data Processing Policy",
        templateCode: "POLICY_PD_PROCESSING",
        documentType: "policy",
        framework: "fz152",
        status: "draft",
        content: `
<h1>ПОЛИТИКА</h1>
<h2>в области обработки персональных данных</h2>

<p><strong>ООО «Демо Компания»</strong></p>
<p>ИНН: 7707083893</p>

<h3>1. ОБЩИЕ ПОЛОЖЕНИЯ</h3>

<p>1.1. Настоящая Политика в области обработки персональных данных (далее — Политика) разработана в соответствии с:</p>
<ul>
<li>Конституцией Российской Федерации;</li>
<li>Федеральным законом от 27.07.2006 № 152-ФЗ «О персональных данных»;</li>
<li>Постановлением Правительства РФ от 01.11.2012 № 1119;</li>
<li>Приказом ФСТЭК России от 18.02.2013 № 21;</li>
</ul>

<p>1.2. Политика определяет порядок обработки персональных данных и меры по обеспечению безопасности персональных данных в ООО «Демо Компания» (далее — Оператор).</p>

<h3>2. ОСНОВНЫЕ ПОНЯТИЯ</h3>

<p><strong>Персональные данные</strong> — любая информация, относящаяся к прямо или косвенно определенному или определяемому физическому лицу (субъекту персональных данных).</p>

<p><strong>Обработка персональных данных</strong> — любое действие (операция) или совокупность действий (операций), совершаемых с использованием средств автоматизации или без использования таких средств с персональными данными.</p>

<p><strong>Оператор</strong> — государственный орган, муниципальный орган, юридическое или физическое лицо, самостоятельно или совместно с другими лицами организующие и (или) осуществляющие обработку персональных данных.</p>

<h3>3. ПРИНЦИПЫ ОБРАБОТКИ ПЕРСОНАЛЬНЫХ ДАННЫХ</h3>

<p>3.1. Обработка персональных данных осуществляется на законной и справедливой основе.</p>

<p>3.2. Обработка персональных данных ограничивается достижением конкретных, заранее определенных и законных целей.</p>

<p>3.3. Не допускается объединение баз данных, содержащих персональные данные, обработка которых осуществляется в целях, несовместимых между собой.</p>

<h3>4. ЦЕЛИ ОБРАБОТКИ ПЕРСОНАЛЬНЫХ ДАННЫХ</h3>

<p>4.1. Оператор обрабатывает персональные данные в следующих целях:</p>
<ul>
<li>Исполнение трудового договора с работниками;</li>
<li>Исполнение договоров с контрагентами;</li>
<li>Ведение кадрового и бухгалтерского учета;</li>
<li>Обеспечение пропускного режима;</li>
<li>Исполнение требований законодательства.</li>
</ul>

<h3>5. КАТЕГОРИИ СУБЪЕКТОВ ПЕРСОНАЛЬНЫХ ДАННЫХ</h3>

<p>5.1. Оператор обрабатывает персональные данные следующих категорий субъектов:</p>
<ul>
<li>Работники Оператора;</li>
<li>Кандидаты на замещение вакантных должностей;</li>
<li>Контрагенты — физические лица;</li>
<li>Представители контрагентов — юридических лиц;</li>
<li>Посетители.</li>
</ul>

<h3>6. ПРАВА СУБЪЕКТОВ ПЕРСОНАЛЬНЫХ ДАННЫХ</h3>

<p>6.1. Субъект персональных данных имеет право:</p>
<ul>
<li>Получать информацию об обработке своих персональных данных;</li>
<li>Требовать уточнения, блокирования или уничтожения персональных данных;</li>
<li>Отозвать согласие на обработку персональных данных;</li>
<li>Обжаловать действия Оператора в Роскомнадзор или в суд.</li>
</ul>

<h3>7. МЕРЫ ПО ОБЕСПЕЧЕНИЮ БЕЗОПАСНОСТИ</h3>

<p>7.1. Оператор принимает следующие меры по обеспечению безопасности персональных данных:</p>
<ul>
<li>Назначение ответственного за организацию обработки персональных данных;</li>
<li>Издание локальных актов по вопросам обработки персональных данных;</li>
<li>Применение организационных и технических мер;</li>
<li>Оценка эффективности принимаемых мер;</li>
<li>Обнаружение фактов несанкционированного доступа;</li>
<li>Восстановление персональных данных;</li>
<li>Контроль за принимаемыми мерами.</li>
</ul>

<h3>8. ЗАКЛЮЧИТЕЛЬНЫЕ ПОЛОЖЕНИЯ</h3>

<p>8.1. Настоящая Политика вступает в силу с момента ее утверждения и действует бессрочно до замены ее новой Политикой.</p>

<p>8.2. Политика подлежит пересмотру в случае изменения законодательства Российской Федерации в области персональных данных.</p>

<hr/>

<p><strong>УТВЕРЖДАЮ</strong></p>
<p>Генеральный директор</p>
<p>_________________ / _________________ /</p>
<p>«____» _____________ 2024 г.</p>
        `.trim(),
        companyId: "1",
        companyName: "ООО «Демо Компания»",
        createdAt: "2024-01-15T10:00:00Z",
        updatedAt: "2024-01-15T10:00:00Z",
        version: 1,
        approvedBy: null,
        approvedAt: null,
        formData: {
          company_name: "ООО «Демо Компания»",
          inn: "7707083893",
          director_name: "Иванов Иван Иванович",
        },
      };
    },
    enabled: !!id,
  });

  // Document versions (mock)
  const versions: DocumentVersion[] = [
    {
      id: "v1",
      version: 1,
      content: document?.content || "",
      changedBy: "Система",
      changedAt: "2024-01-15T10:00:00Z",
      comment: "Первоначальная версия",
    },
  ];

  useEffect(() => {
    if (document?.content) {
      setEditedContent(document.content);
    }
  }, [document?.content]);

  // Save document mutation
  const saveMutation = useMutation({
    mutationFn: async (content: string) => {
      // In production this would call the API
      await new Promise((resolve) => setTimeout(resolve, 500));
      return { success: true };
    },
    onSuccess: () => {
      setHasUnsavedChanges(false);
      setIsEditing(false);
      queryClient.invalidateQueries({ queryKey: ["document", id] });
    },
  });

  // Export handlers
  const handleExportWord = async () => {
    // Create a simple Word-compatible HTML file
    const htmlContent = `
      <!DOCTYPE html>
      <html xmlns:o="urn:schemas-microsoft-com:office:office"
            xmlns:w="urn:schemas-microsoft-com:office:word">
      <head>
        <meta charset="utf-8">
        <title>${document?.title}</title>
        <style>
          body { font-family: 'Times New Roman', serif; font-size: 14pt; }
          h1 { font-size: 18pt; text-align: center; }
          h2 { font-size: 16pt; text-align: center; }
          h3 { font-size: 14pt; margin-top: 20pt; }
          p { text-indent: 1cm; text-align: justify; }
          ul { margin-left: 2cm; }
        </style>
      </head>
      <body>
        ${editedContent}
      </body>
      </html>
    `;

    const blob = new Blob([htmlContent], { type: "application/msword" });
    const url = URL.createObjectURL(blob);
    const a = window.document.createElement("a");
    a.href = url;
    a.download = `${document?.templateCode || "document"}.doc`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleExportPdf = () => {
    // Open print dialog for PDF
    window.print();
  };

  const handlePrint = () => {
    window.print();
  };

  const handleContentChange = (e: React.FormEvent<HTMLDivElement>) => {
    const newContent = e.currentTarget.innerHTML;
    setEditedContent(newContent);
    setHasUnsavedChanges(true);
  };

  const handleSave = () => {
    saveMutation.mutate(editedContent);
  };

  const handleRestoreVersion = (version: DocumentVersion) => {
    setEditedContent(version.content);
    setHasUnsavedChanges(true);
    setSelectedVersion(null);
    setShowVersions(false);
  };

  const statusColors = {
    draft: "bg-yellow-100 text-yellow-800",
    review: "bg-blue-100 text-blue-800",
    approved: "bg-green-100 text-green-800",
    expired: "bg-red-100 text-red-800",
  };

  const statusLabels = {
    draft: "Черновик",
    review: "На рассмотрении",
    approved: "Утверждён",
    expired: "Истёк срок",
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!document) {
    return (
      <div className="text-center py-12">
        <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Документ не найден</h3>
        <p className="mt-1 text-sm text-gray-500">
          Документ с указанным идентификатором не существует.
        </p>
        <button
          onClick={() => navigate(-1)}
          className="mt-4 text-blue-600 hover:text-blue-700"
        >
          Вернуться назад
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <button
                onClick={() => navigate(-1)}
                className="mr-4 p-2 text-gray-400 hover:text-gray-500 rounded-md hover:bg-gray-100"
              >
                <ArrowLeftIcon className="h-5 w-5" />
              </button>
              <div>
                <h1 className="text-lg font-medium text-gray-900">{document.title}</h1>
                <div className="flex items-center space-x-2 text-sm text-gray-500">
                  <span>{document.templateCode}</span>
                  <span>•</span>
                  <span
                    className={`px-2 py-0.5 rounded-full text-xs ${
                      statusColors[document.status as keyof typeof statusColors]
                    }`}
                  >
                    {statusLabels[document.status as keyof typeof statusLabels]}
                  </span>
                  <span>•</span>
                  <span>Версия {document.version}</span>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              {hasUnsavedChanges && (
                <span className="flex items-center text-sm text-amber-600">
                  <ExclamationTriangleIcon className="h-4 w-4 mr-1" />
                  Есть несохранённые изменения
                </span>
              )}

              <button
                onClick={() => setShowVersions(!showVersions)}
                className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 flex items-center"
              >
                <ClockIcon className="h-4 w-4 mr-1" />
                История
              </button>

              {isEditing ? (
                <>
                  <button
                    onClick={() => {
                      setEditedContent(document.content);
                      setHasUnsavedChanges(false);
                      setIsEditing(false);
                    }}
                    className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                  >
                    Отмена
                  </button>
                  <button
                    onClick={handleSave}
                    disabled={saveMutation.isPending}
                    className="px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 flex items-center disabled:opacity-50"
                  >
                    {saveMutation.isPending ? (
                      <ArrowPathIcon className="h-4 w-4 mr-1 animate-spin" />
                    ) : (
                      <CheckIcon className="h-4 w-4 mr-1" />
                    )}
                    Сохранить
                  </button>
                </>
              ) : (
                <button
                  onClick={() => setIsEditing(true)}
                  className="px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 flex items-center"
                >
                  <PencilIcon className="h-4 w-4 mr-1" />
                  Редактировать
                </button>
              )}

              <div className="border-l pl-2 ml-2 flex items-center space-x-1">
                <button
                  onClick={handleExportWord}
                  className="p-2 text-gray-400 hover:text-gray-500 rounded-md hover:bg-gray-100"
                  title="Скачать Word"
                >
                  <ArrowDownTrayIcon className="h-5 w-5" />
                </button>
                <button
                  onClick={handlePrint}
                  className="p-2 text-gray-400 hover:text-gray-500 rounded-md hover:bg-gray-100"
                  title="Печать"
                >
                  <PrinterIcon className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex gap-6">
          {/* Main content */}
          <div className="flex-1">
            <div className="bg-white shadow rounded-lg overflow-hidden">
              {/* Document metadata */}
              <div className="border-b px-6 py-4 bg-gray-50">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Организация:</span>
                    <p className="font-medium">{document.companyName}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Тип документа:</span>
                    <p className="font-medium capitalize">{document.documentType}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Создан:</span>
                    <p className="font-medium">
                      {new Date(document.createdAt).toLocaleDateString("ru-RU")}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-500">Изменён:</span>
                    <p className="font-medium">
                      {new Date(document.updatedAt).toLocaleDateString("ru-RU")}
                    </p>
                  </div>
                </div>
              </div>

              {/* Editor area */}
              <div
                ref={editorRef}
                className={`p-8 min-h-[600px] prose prose-sm max-w-none ${
                  isEditing ? "bg-blue-50/30" : ""
                }`}
                contentEditable={isEditing}
                onInput={handleContentChange}
                dangerouslySetInnerHTML={{ __html: editedContent }}
                style={{
                  outline: isEditing ? "2px dashed #3b82f6" : "none",
                  outlineOffset: "-4px",
                }}
              />
            </div>
          </div>

          {/* Version history sidebar */}
          {showVersions && (
            <div className="w-80 flex-shrink-0">
              <div className="bg-white shadow rounded-lg p-4">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  История версий
                </h3>
                <div className="space-y-3">
                  {versions.map((version) => (
                    <div
                      key={version.id}
                      className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                        selectedVersion?.id === version.id
                          ? "border-blue-500 bg-blue-50"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                      onClick={() => setSelectedVersion(version)}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-medium">Версия {version.version}</span>
                        <span className="text-xs text-gray-500">
                          {new Date(version.changedAt).toLocaleDateString("ru-RU")}
                        </span>
                      </div>
                      <p className="text-sm text-gray-500 mt-1">{version.comment}</p>
                      <p className="text-xs text-gray-400 mt-1">
                        Автор: {version.changedBy}
                      </p>
                      {selectedVersion?.id === version.id && (
                        <div className="mt-2 flex space-x-2">
                          <button
                            onClick={() => handleRestoreVersion(version)}
                            className="text-xs text-blue-600 hover:text-blue-700"
                          >
                            Восстановить
                          </button>
                          <button
                            onClick={() => setSelectedVersion(null)}
                            className="text-xs text-gray-500 hover:text-gray-600"
                          >
                            Отмена
                          </button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Print styles */}
      <style>{`
        @media print {
          body * {
            visibility: hidden;
          }
          .prose, .prose * {
            visibility: visible;
          }
          .prose {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            padding: 2cm;
          }
        }
      `}</style>
    </div>
  );
}
