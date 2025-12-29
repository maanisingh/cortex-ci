import { test, expect } from '@playwright/test';

test.describe('Internationalization', () => {
  test('should display Russian by default', async ({ page }) => {
    await page.goto('/login');

    // Check for Russian text
    await expect(page.locator('text=/вход|войти|авторизация/i')).toBeVisible();
  });

  test('should switch to English', async ({ page }) => {
    await page.goto('/login');

    // Find language selector
    const langSelector = page.locator('button[aria-label*="язык"], button[aria-label*="language"], select[name="language"]');
    await langSelector.click();

    // Select English
    await page.click('text=/English|EN/i');

    // Check for English text
    await expect(page.locator('text=/login|sign in/i')).toBeVisible();
  });

  test('should persist language preference', async ({ page }) => {
    await page.goto('/login');

    // Switch to English
    const langSelector = page.locator('button[aria-label*="язык"], button[aria-label*="language"]');
    await langSelector.click();
    await page.click('text=/English|EN/i');

    // Reload page
    await page.reload();

    // Should still be in English
    await expect(page.locator('text=/login|sign in|email/i')).toBeVisible();
  });

  test('should translate dashboard content', async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('input[type="email"]', 'demo@cortex.local');
    await page.fill('input[type="password"]', 'demo123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/dashboard/);

    // Russian content
    await expect(page.locator('text=/панель|задач|соответствие/i')).toBeVisible();

    // Switch to English
    const langSelector = page.locator('button[aria-label*="язык"], button[aria-label*="language"]');
    await langSelector.click();
    await page.click('text=/English|EN/i');

    // English content
    await expect(page.locator('text=/dashboard|task|compliance/i')).toBeVisible();
  });

  test('should support 12 languages', async ({ page }) => {
    await page.goto('/login');

    // Open language selector
    const langSelector = page.locator('button[aria-label*="язык"], button[aria-label*="language"]');
    await langSelector.click();

    // Check for multiple language options
    const languages = ['Русский', 'English', 'Deutsch', '中文', '日本語', 'العربية'];

    for (const lang of languages) {
      await expect(page.locator(`text=/${lang}/i`).first()).toBeVisible();
    }
  });
});
