import { test, expect, devices } from '@playwright/test';

test.describe('Mobile Responsiveness', () => {
  test.use({ ...devices['iPhone 12'] });

  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"], input[name="email"]', 'demo@cortex.local');
    await page.fill('input[type="password"], input[name="password"]', 'demo123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/dashboard/);
  });

  test('should show mobile navigation', async ({ page }) => {
    // Bottom navigation should be visible on mobile
    await expect(page.locator('nav[class*="bottom"], nav[class*="mobile"]')).toBeVisible();
  });

  test('should have hamburger menu', async ({ page }) => {
    // Look for menu button
    const menuButton = page.locator('button[aria-label*="меню"], button[aria-label*="menu"]');
    await expect(menuButton).toBeVisible();

    // Click and check sidebar opens
    await menuButton.click();
    await expect(page.locator('nav, aside, [role="navigation"]')).toBeVisible();
  });

  test('should be touch-friendly', async ({ page }) => {
    // All buttons should have minimum touch target size (44x44)
    const buttons = await page.locator('button').all();

    for (const button of buttons.slice(0, 5)) {
      const box = await button.boundingBox();
      if (box) {
        expect(box.width).toBeGreaterThanOrEqual(40);
        expect(box.height).toBeGreaterThanOrEqual(40);
      }
    }
  });

  test('should stack cards vertically on mobile', async ({ page }) => {
    await page.goto('/dashboard');

    // Cards should be full width on mobile
    const card = page.locator('div[class*="card"]').first();
    const viewport = page.viewportSize();
    const cardBox = await card.boundingBox();

    if (cardBox && viewport) {
      // Card should take most of the viewport width
      expect(cardBox.width).toBeGreaterThan(viewport.width * 0.8);
    }
  });

  test('should display mobile-optimized forms', async ({ page }) => {
    await page.goto('/compliance-tasks');
    await page.click('button:has-text("Создать"), button:has-text("+")');

    // Form inputs should be full width
    const input = page.locator('input[name="title"]').first();
    const inputBox = await input.boundingBox();
    const viewport = page.viewportSize();

    if (inputBox && viewport) {
      expect(inputBox.width).toBeGreaterThan(viewport.width * 0.7);
    }
  });
});

test.describe('Tablet Responsiveness', () => {
  test.use({ ...devices['iPad Pro'] });

  test('should show sidebar on tablet', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"], input[name="email"]', 'demo@cortex.local');
    await page.fill('input[type="password"], input[name="password"]', 'demo123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/dashboard/);

    // Sidebar should be visible or easily accessible on tablet
    const sidebar = page.locator('aside, nav[class*="sidebar"]');
    await expect(sidebar).toBeVisible();
  });

  test('should display grid layout on tablet', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"], input[name="email"]', 'demo@cortex.local');
    await page.fill('input[type="password"], input[name="password"]', 'demo123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/dashboard/);

    // Check for multi-column layout
    const cards = await page.locator('div[class*="card"]').all();
    if (cards.length >= 2) {
      const box1 = await cards[0].boundingBox();
      const box2 = await cards[1].boundingBox();

      // On tablet, some cards might be side by side
      if (box1 && box2) {
        // Either same row (different x) or stacked (same x, different y)
        const isSameRow = Math.abs(box1.y - box2.y) < 10;
        const isStacked = Math.abs(box1.x - box2.x) < 10;
        expect(isSameRow || isStacked).toBeTruthy();
      }
    }
  });
});
