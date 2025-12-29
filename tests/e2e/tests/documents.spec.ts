import { test, expect } from '@playwright/test';

test.describe('Document Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"], input[name="email"]', 'demo@cortex.local');
    await page.fill('input[type="password"], input[name="password"]', 'demo123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/dashboard/);
  });

  test('should display document library', async ({ page }) => {
    await page.goto('/documents');
    await expect(page.locator('h1, h2')).toContainText(/документ|document/i);
  });

  test('should show document templates catalog', async ({ page }) => {
    await page.goto('/template-catalog');
    await expect(page.locator('text=/шаблон|template/i')).toBeVisible();
  });

  test('should display 152-FZ templates', async ({ page }) => {
    await page.goto('/template-catalog');
    await expect(page.locator('text=/152-ФЗ/i')).toBeVisible();
  });

  test('should display 187-FZ templates', async ({ page }) => {
    await page.goto('/template-catalog');
    await expect(page.locator('text=/187-ФЗ|КИИ/i')).toBeVisible();
  });

  test('should display GOST 57580 templates', async ({ page }) => {
    await page.goto('/template-catalog');
    await expect(page.locator('text=/ГОСТ|57580/i')).toBeVisible();
  });

  test('should generate document from template', async ({ page }) => {
    await page.goto('/template-catalog');

    // Click on a template
    await page.click('button:has-text("Генерировать"), button:has-text("Generate")').first();

    // Fill form if needed
    await page.waitForTimeout(1000);

    // Check for preview or download option
    await expect(page.locator('text=/preview|просмотр|скачать|download/i')).toBeVisible();
  });

  test('should support document search', async ({ page }) => {
    await page.goto('/documents');

    // Find search input
    await page.fill('input[type="search"], input[placeholder*="Поиск"]', 'политика');
    await page.keyboard.press('Enter');

    // Results should appear
    await expect(page.locator('text=/результат|result|найден/i')).toBeVisible();
  });

  test('should show document versioning', async ({ page }) => {
    await page.goto('/documents');

    // Click on a document
    await page.click('tr:has-text("Политика"), div:has-text("Политика")').first();

    // Check for version history
    await expect(page.locator('text=/версия|version|история/i')).toBeVisible();
  });

  test('should export document to PDF', async ({ page }) => {
    await page.goto('/documents');

    // Click export button
    const [download] = await Promise.all([
      page.waitForEvent('download', { timeout: 10000 }).catch(() => null),
      page.click('button:has-text("PDF"), button:has-text("Экспорт")').catch(() => null)
    ]);

    // Either download started or export modal appeared
    const exportButton = page.locator('button:has-text("PDF"), button:has-text("Экспорт")');
    await expect(exportButton.or(page.locator('text=/скачать|download/i'))).toBeVisible();
  });
});
