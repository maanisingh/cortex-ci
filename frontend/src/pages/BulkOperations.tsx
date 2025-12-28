import { useState, useRef } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../services/api";
import {
  ArrowUpTrayIcon,
  ArrowDownTrayIcon,
  DocumentArrowUpIcon,
  DocumentArrowDownIcon,
  TableCellsIcon,
  DocumentTextIcon,
  DocumentChartBarIcon,
  CheckCircleIcon,
  XCircleIcon,
  ArrowPathIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";

interface BulkOperation {
  operation_id: string;
  operation_type: string;
  status: string;
  total_items: number;
  processed_items: number;
  successful_items: number;
  failed_items: number;
  progress_percentage: number;
  errors: Array<{ row?: number; item?: string; error: string }>;
  started_at: string;
  completed_at?: string;
  duration_seconds?: number;
}

const EXPORT_FORMATS = [
  {
    value: "csv",
    label: "CSV",
    icon: TableCellsIcon,
    description: "Comma-separated values",
  },
  {
    value: "json",
    label: "JSON",
    icon: DocumentTextIcon,
    description: "JavaScript Object Notation",
  },
  {
    value: "xlsx",
    label: "Excel",
    icon: DocumentChartBarIcon,
    description: "Microsoft Excel format",
  },
  {
    value: "pdf",
    label: "PDF",
    icon: DocumentArrowDownIcon,
    description: "Portable Document Format",
  },
];

export default function BulkOperations() {
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);

  // State
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [importType, setImportType] = useState<"csv" | "json">("csv");
  const [skipDuplicates, setSkipDuplicates] = useState(true);
  const [updateExisting, setUpdateExisting] = useState(false);
  const [exportFormat, setExportFormat] = useState<string>("csv");
  const [exportType, setExportType] = useState<string>("entities");

  // Fetch recent operations
  const { data: operations } = useQuery<BulkOperation[]>({
    queryKey: ["bulk-operations"],
    queryFn: async () => {
      const response = await api.get("/bulk/operations");
      return response.data.operations || [];
    },
    refetchInterval: 5000, // Refresh every 5 seconds
  });

  // Import mutation
  const importMutation = useMutation({
    mutationFn: async (formData: FormData) => {
      const response = await api.post("/bulk/import/entities", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        params: {
          skip_duplicates: skipDuplicates,
          update_existing: updateExisting,
        },
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bulk-operations"] });
      queryClient.invalidateQueries({ queryKey: ["entities"] });
      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    },
  });

  // Export mutation
  const exportMutation = useMutation({
    mutationFn: async () => {
      const response = await api.get(`/export/${exportType}`, {
        params: { format: exportFormat },
        responseType:
          exportFormat === "pdf" || exportFormat === "xlsx" ? "blob" : "json",
      });
      return response.data;
    },
    onSuccess: (data) => {
      // Handle file download
      if (data instanceof Blob) {
        const url = URL.createObjectURL(data);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${exportType}_export.${exportFormat}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } else if (data.content) {
        const blob = new Blob([data.content], { type: data.content_type });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = data.filename || `${exportType}_export.${exportFormat}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
    },
  });

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setImportType(file.name.endsWith(".json") ? "json" : "csv");
    }
  };

  const handleImport = () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append("file", selectedFile);
    importMutation.mutate(formData);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "text-green-600 bg-green-50";
      case "processing":
        return "text-blue-600 bg-blue-50";
      case "failed":
        return "text-red-600 bg-red-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case "processing":
        return <ArrowPathIcon className="h-5 w-5 text-blue-500 animate-spin" />;
      case "failed":
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <ExclamationTriangleIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <ArrowUpTrayIcon className="h-7 w-7 text-indigo-600" />
          Bulk Operations
        </h1>
        <p className="mt-2 text-sm text-gray-700">
          Import, export, and manage data in bulk
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Import Section */}
        <div className="card">
          <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center gap-2">
            <DocumentArrowUpIcon className="h-5 w-5 text-indigo-600" />
            Bulk Import
          </h2>
          <p className="text-sm text-gray-600 mb-4">
            Import entities from CSV or JSON files. Supports up to 10,000
            records per import.
          </p>

          {/* File Upload Area */}
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-indigo-400 transition-colors">
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv,.json"
              onChange={handleFileSelect}
              className="hidden"
              id="file-upload"
            />
            <label htmlFor="file-upload" className="cursor-pointer">
              <ArrowUpTrayIcon className="h-12 w-12 mx-auto text-gray-400 mb-2" />
              {selectedFile ? (
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {selectedFile.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {(selectedFile.size / 1024).toFixed(1)} KB -{" "}
                    {importType.toUpperCase()}
                  </p>
                </div>
              ) : (
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    Drop your file here, or click to browse
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    Supports CSV and JSON files
                  </p>
                </div>
              )}
            </label>
          </div>

          {/* Import Options */}
          <div className="mt-4 space-y-3">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={skipDuplicates}
                onChange={(e) => setSkipDuplicates(e.target.checked)}
                className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
              <span className="text-sm text-gray-700">
                Skip duplicate entities
              </span>
            </label>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={updateExisting}
                onChange={(e) => setUpdateExisting(e.target.checked)}
                className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
              <span className="text-sm text-gray-700">
                Update existing entities
              </span>
            </label>
          </div>

          <button
            onClick={handleImport}
            disabled={!selectedFile || importMutation.isPending}
            className="btn btn-primary w-full mt-4"
          >
            {importMutation.isPending ? (
              <>
                <ArrowPathIcon className="h-4 w-4 mr-2 animate-spin" />
                Importing...
              </>
            ) : (
              <>
                <ArrowUpTrayIcon className="h-4 w-4 mr-2" />
                Start Import
              </>
            )}
          </button>

          {importMutation.isError && (
            <p className="mt-2 text-sm text-red-600">
              Import failed. Please check your file format.
            </p>
          )}
        </div>

        {/* Export Section */}
        <div className="card">
          <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center gap-2">
            <ArrowDownTrayIcon className="h-5 w-5 text-indigo-600" />
            Export Data
          </h2>
          <p className="text-sm text-gray-600 mb-4">
            Export your data in multiple formats for analysis or backup.
          </p>

          {/* Data Type Selection */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Data to Export
            </label>
            <select
              value={exportType}
              onChange={(e) => setExportType(e.target.value)}
              className="input"
            >
              <option value="entities">Entities</option>
              <option value="constraints">Constraints</option>
              <option value="audit_logs">Audit Logs</option>
              <option value="risk_report">Risk Report</option>
            </select>
          </div>

          {/* Format Selection */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Export Format
            </label>
            <div className="grid grid-cols-2 gap-2">
              {EXPORT_FORMATS.map((format) => (
                <button
                  key={format.value}
                  onClick={() => setExportFormat(format.value)}
                  className={`flex items-center gap-2 p-3 rounded-lg border transition-all ${
                    exportFormat === format.value
                      ? "border-indigo-500 bg-indigo-50 text-indigo-700"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                >
                  <format.icon className="h-5 w-5" />
                  <div className="text-left">
                    <p className="text-sm font-medium">{format.label}</p>
                    <p className="text-xs text-gray-500">
                      {format.description}
                    </p>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={() => exportMutation.mutate()}
            disabled={exportMutation.isPending}
            className="btn btn-secondary w-full"
          >
            {exportMutation.isPending ? (
              <>
                <ArrowPathIcon className="h-4 w-4 mr-2 animate-spin" />
                Exporting...
              </>
            ) : (
              <>
                <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
                Export{" "}
                {exportType
                  .replace("_", " ")
                  .replace(/\b\w/g, (l) => l.toUpperCase())}
              </>
            )}
          </button>
        </div>
      </div>

      {/* Recent Operations */}
      <div className="card mt-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">
          Recent Operations
        </h2>
        {operations && operations.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Status
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Type
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Progress
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Results
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Started
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Duration
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {operations.map((op) => (
                  <tr key={op.operation_id}>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(op.status)}
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getStatusColor(
                            op.status,
                          )}`}
                        >
                          {op.status}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 capitalize">
                      {op.operation_type}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-indigo-600 h-2 rounded-full transition-all"
                            style={{ width: `${op.progress_percentage}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-500">
                          {op.progress_percentage.toFixed(0)}%
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm">
                      <span className="text-green-600">
                        {op.successful_items} success
                      </span>
                      {op.failed_items > 0 && (
                        <span className="text-red-600 ml-2">
                          {op.failed_items} failed
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                      {op.started_at
                        ? new Date(op.started_at).toLocaleString()
                        : "-"}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                      {op.duration_seconds
                        ? `${op.duration_seconds.toFixed(1)}s`
                        : "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">
            No recent operations. Start an import or export above.
          </p>
        )}
      </div>

      {/* Template Downloads */}
      <div className="card mt-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">
          Import Templates
        </h2>
        <p className="text-sm text-gray-600 mb-4">
          Download template files to get started with bulk imports.
        </p>
        <div className="flex gap-4">
          <a
            href="/templates/entities_template.csv"
            download
            className="btn btn-secondary"
          >
            <DocumentTextIcon className="h-4 w-4 mr-2" />
            CSV Template
          </a>
          <a
            href="/templates/entities_template.json"
            download
            className="btn btn-secondary"
          >
            <DocumentTextIcon className="h-4 w-4 mr-2" />
            JSON Template
          </a>
        </div>
      </div>
    </div>
  );
}
