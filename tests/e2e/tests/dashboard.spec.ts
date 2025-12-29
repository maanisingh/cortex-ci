import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[type="email"], input[name="email"]', 'demo@cortex.local');
    await page.fill('input[type="password"], input[name="password"]', 'demo123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/dashboard/);
  });

  test('should display dashboard with key metrics', async ({ page }) => {
    await expect(page.locator('h1, h2').first()).toContainText(/dashboard|панель/i);

    // Check for compliance score widget
    await expect(page.locator('text=/соответствие|compliance/i')).toBeVisible();

    // Check for task count
    await expect(page.locator('text=/задач|tasks/i')).toBeVisible();
  });

  test('should display compliance score chart', async ({ page }) => {
    // Look for chart or graph element
    const chart = page.locator('canvas, svg[class*="chart"], div[class*="chart"]');
    await expect(chart.first()).toBeVisible();
  });

  test('should show risk heat map', async ({ page }) => {
    await expect(page.locator('text=/риск|risk/i')).toBeVisible();
  });

  test('should navigate to tasks from dashboard', async ({ page }) => {
    await page.click('a[href*="task"], button:has-text("Задачи")');
    await expect(page).toHaveURL(/task/);
  });

  test('should show upcoming deadlines', async ({ page }) => {
    await expect(page.locator('text=/срок|deadline|календарь/i')).toBeVisible();
  });

  test('should support dark mode toggle', async ({ page }) => {
    const themeToggle = page.locator('button[aria-label*="тема"], button[aria-label*="theme"]');
    await themeToggle.click();

    // Check if dark class is applied
    await expect(page.locator('html, body, .dark')).toHaveClass(/dark/);
  });
});
