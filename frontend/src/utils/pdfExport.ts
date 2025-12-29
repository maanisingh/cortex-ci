// PDF Export utility for compliance reports
// Uses browser print functionality with custom styles

interface ComplianceReportData {
  companyName: string;
  companyInn: string;
  generatedAt: Date;
  overallScore: number;
  frameworks: {
    name: string;
    score: number;
    completed: number;
    total: number;
  }[];
  documentStats: {
    total: number;
    approved: number;
    draft: number;
    expired: number;
  };
  taskStats: {
    total: number;
    completed: number;
    inProgress: number;
    overdue: number;
  };
  auditReadiness: {
    score: number;
    categories: {
      name: string;
      score: number;
    }[];
  };
  risks: {
    name: string;
    level: string;
    category: string;
  }[];
}

export function generateComplianceReportHTML(data: ComplianceReportData): string {
  const getScoreColor = (score: number) => {
    if (score >= 80) return "#22c55e";
    if (score >= 60) return "#eab308";
    if (score >= 40) return "#f97316";
    return "#ef4444";
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return "Отлично";
    if (score >= 60) return "Хорошо";
    if (score >= 40) return "Требует внимания";
    return "Критично";
  };

  return `
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Отчёт о соответствии - ${data.companyName}</title>
  <style>
    @page { margin: 2cm; size: A4; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      color: #1f2937;
      line-height: 1.6;
      padding: 0;
      margin: 0;
    }
    .header {
      text-align: center;
      border-bottom: 2px solid #3b82f6;
      padding-bottom: 20px;
      margin-bottom: 30px;
    }
    .header h1 { margin: 0; color: #1e40af; font-size: 24px; }
    .header p { margin: 5px 0; color: #6b7280; }
    .section { margin-bottom: 30px; }
    .section h2 {
      color: #1e40af;
      font-size: 18px;
      border-bottom: 1px solid #e5e7eb;
      padding-bottom: 10px;
      margin-bottom: 15px;
    }
    .score-card {
      display: inline-block;
      background: #f3f4f6;
      padding: 15px 25px;
      border-radius: 8px;
      text-align: center;
      margin: 10px;
    }
    .score-value {
      font-size: 36px;
      font-weight: bold;
    }
    .score-label {
      font-size: 14px;
      color: #6b7280;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 15px;
    }
    th, td {
      padding: 10px;
      text-align: left;
      border-bottom: 1px solid #e5e7eb;
    }
    th { background: #f9fafb; font-weight: 600; }
    .progress-bar {
      height: 8px;
      background: #e5e7eb;
      border-radius: 4px;
      overflow: hidden;
    }
    .progress-fill {
      height: 100%;
      border-radius: 4px;
    }
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 15px;
    }
    .stat-item {
      background: #f9fafb;
      padding: 15px;
      border-radius: 8px;
      text-align: center;
    }
    .stat-value { font-size: 24px; font-weight: bold; }
    .stat-label { font-size: 12px; color: #6b7280; }
    .footer {
      margin-top: 40px;
      padding-top: 20px;
      border-top: 1px solid #e5e7eb;
      text-align: center;
      color: #9ca3af;
      font-size: 12px;
    }
    @media print {
      .no-print { display: none; }
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>CORTEX GRC - Отчёт о соответствии</h1>
    <p><strong>${data.companyName}</strong></p>
    <p>ИНН: ${data.companyInn}</p>
    <p>Дата формирования: ${data.generatedAt.toLocaleDateString("ru-RU", {
      day: "2-digit",
      month: "long",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })}</p>
  </div>

  <div class="section">
    <h2>Общий уровень соответствия</h2>
    <div class="score-card">
      <div class="score-value" style="color: ${getScoreColor(data.overallScore)}">${data.overallScore}%</div>
      <div class="score-label">${getScoreLabel(data.overallScore)}</div>
    </div>
  </div>

  <div class="section">
    <h2>Соответствие по нормативным рамкам</h2>
    <table>
      <thead>
        <tr>
          <th>Фреймворк</th>
          <th>Прогресс</th>
          <th>Выполнено</th>
          <th>Оценка</th>
        </tr>
      </thead>
      <tbody>
        ${data.frameworks
          .map(
            (fw) => `
          <tr>
            <td>${fw.name}</td>
            <td>
              <div class="progress-bar">
                <div class="progress-fill" style="width: ${fw.score}%; background: ${getScoreColor(fw.score)}"></div>
              </div>
            </td>
            <td>${fw.completed}/${fw.total}</td>
            <td style="color: ${getScoreColor(fw.score)}; font-weight: bold">${fw.score}%</td>
          </tr>
        `
          )
          .join("")}
      </tbody>
    </table>
  </div>

  <div class="section">
    <h2>Статус документации</h2>
    <div class="stats-grid">
      <div class="stat-item">
        <div class="stat-value" style="color: #3b82f6">${data.documentStats.total}</div>
        <div class="stat-label">Всего документов</div>
      </div>
      <div class="stat-item">
        <div class="stat-value" style="color: #22c55e">${data.documentStats.approved}</div>
        <div class="stat-label">Утверждено</div>
      </div>
      <div class="stat-item">
        <div class="stat-value" style="color: #6b7280">${data.documentStats.draft}</div>
        <div class="stat-label">Черновики</div>
      </div>
      <div class="stat-item">
        <div class="stat-value" style="color: #ef4444">${data.documentStats.expired}</div>
        <div class="stat-label">Истёк срок</div>
      </div>
    </div>
  </div>

  <div class="section">
    <h2>Статус задач</h2>
    <div class="stats-grid">
      <div class="stat-item">
        <div class="stat-value" style="color: #3b82f6">${data.taskStats.total}</div>
        <div class="stat-label">Всего задач</div>
      </div>
      <div class="stat-item">
        <div class="stat-value" style="color: #22c55e">${data.taskStats.completed}</div>
        <div class="stat-label">Выполнено</div>
      </div>
      <div class="stat-item">
        <div class="stat-value" style="color: #eab308">${data.taskStats.inProgress}</div>
        <div class="stat-label">В работе</div>
      </div>
      <div class="stat-item">
        <div class="stat-value" style="color: #ef4444">${data.taskStats.overdue}</div>
        <div class="stat-label">Просрочено</div>
      </div>
    </div>
  </div>

  <div class="section">
    <h2>Готовность к аудиту</h2>
    <div class="score-card">
      <div class="score-value" style="color: ${getScoreColor(data.auditReadiness.score)}">${data.auditReadiness.score}%</div>
      <div class="score-label">Общая готовность</div>
    </div>
    <table>
      <thead>
        <tr>
          <th>Категория</th>
          <th>Готовность</th>
        </tr>
      </thead>
      <tbody>
        ${data.auditReadiness.categories
          .map(
            (cat) => `
          <tr>
            <td>${cat.name}</td>
            <td>
              <div style="display: flex; align-items: center; gap: 10px;">
                <div class="progress-bar" style="flex: 1">
                  <div class="progress-fill" style="width: ${cat.score}%; background: ${getScoreColor(cat.score)}"></div>
                </div>
                <span style="color: ${getScoreColor(cat.score)}; font-weight: bold; min-width: 45px">${cat.score}%</span>
              </div>
            </td>
          </tr>
        `
          )
          .join("")}
      </tbody>
    </table>
  </div>

  ${
    data.risks.length > 0
      ? `
  <div class="section">
    <h2>Реестр рисков (${data.risks.length})</h2>
    <table>
      <thead>
        <tr>
          <th>Риск</th>
          <th>Категория</th>
          <th>Уровень</th>
        </tr>
      </thead>
      <tbody>
        ${data.risks
          .slice(0, 10)
          .map(
            (risk) => `
          <tr>
            <td>${risk.name}</td>
            <td>${risk.category}</td>
            <td><strong>${risk.level}</strong></td>
          </tr>
        `
          )
          .join("")}
      </tbody>
    </table>
    ${data.risks.length > 10 ? `<p style="color: #6b7280; font-size: 12px;">и ещё ${data.risks.length - 10} рисков...</p>` : ""}
  </div>
  `
      : ""
  }

  <div class="footer">
    <p>Отчёт сформирован системой CORTEX GRC</p>
    <p>https://cortex.alexandratechlab.com</p>
  </div>
</body>
</html>
  `;
}

export function exportToPDF(data: ComplianceReportData): void {
  const html = generateComplianceReportHTML(data);
  const printWindow = window.open("", "_blank");

  if (printWindow) {
    printWindow.document.write(html);
    printWindow.document.close();

    // Wait for content to load, then trigger print
    printWindow.onload = () => {
      printWindow.print();
    };
  }
}

export function downloadAsHTML(data: ComplianceReportData, filename: string): void {
  const html = generateComplianceReportHTML(data);
  const blob = new Blob([html], { type: "text/html;charset=utf-8" });
  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
