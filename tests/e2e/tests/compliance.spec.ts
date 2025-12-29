import { test, expect } from '@playwright/test';

test.describe('Compliance Features', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"], input[name="email"]', 'demo@cortex.local');
    await page.fill('input[type="password"], input[name="password"]', 'demo123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/dashboard/);
  });

  test('should display 152-FZ compliance page', async ({ page }) => {
    await page.goto('/russian-compliance');
    await expect(page.locator('text=/152-ФЗ|персональн/i')).toBeVisible();
  });

  test('should show compliance frameworks list', async ({ page }) => {
    await page.goto('/russian-compliance');

    // Check for major Russian frameworks
    await expect(page.locator('text=/152-ФЗ/i')).toBeVisible();
  });

  test('should display gap analysis tool', async ({ page }) => {
    await page.goto('/gap-analysis');
    await expect(page.locator('h1, h2')).toContainText(/gap|анализ/i);
  });

  test('should run gap analysis', async ({ page }) => {
    await page.goto('/gap-analysis');

    // Select framework
    await page.click('select, [role="combobox"]');
    await page.click('text=/152-ФЗ/i');

    // Run analysis
    await page.click('button:has-text("Анализ"), button:has-text("Run")');

    // Wait for results
    await expect(page.locator('text=/результат|result|gap/i')).toBeVisible({ timeout: 30000 });
  });

  test('should display control mapping', async ({ page }) => {
    await page.goto('/controls');
    await expect(page.locator('text=/контрол|control/i')).toBeVisible();
  });

  test('should show audit checklists', async ({ page }) => {
    await page.goto('/audit-checklists');
    await expect(page.locator('text=/чеклист|checklist|аудит/i')).toBeVisible();
  });

  test('should display evidence collection', async ({ page }) => {
    await page.goto('/evidence');
    await expect(page.locator('text=/свидетельств|evidence/i')).toBeVisible();
  });
});
