import { test, expect } from '@playwright/test';

const BASE_URL = 'https://cortex.alexandratechlab.com';

test.describe('GRC Platform Navigation', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input#tenant', 'default');
    await page.fill('input#email', 'admin@cortex.io');
    await page.fill('input#password', 'Admin123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard', { timeout: 15000 });
  });

  test('GRC Dashboard loads with updated branding', async ({ page }) => {
    await page.waitForLoadState('networkidle');

    // Check for GRC branding in sidebar
    const sidebarBrand = page.locator('text=CORTEX').first();
    await expect(sidebarBrand).toBeVisible();

    // Check dashboard title
    const dashboardTitle = page.locator('h1:has-text("GRC Dashboard")');
    await expect(dashboardTitle).toBeVisible();

    await page.screenshot({ path: 'audit/grc-01-dashboard.png', fullPage: true });
  });

  test('Risk Management navigation works', async ({ page }) => {
    // Check Risk Register link
    await page.click('text=Risk Register');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'audit/grc-02-risk-register.png', fullPage: true });

    // Check Risk Objects link
    await page.click('text=Risk Objects');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'audit/grc-03-risk-objects.png', fullPage: true });
  });

  test('Compliance navigation works', async ({ page }) => {
    // Check Compliance Dashboard
    await page.click('text=Compliance Dashboard');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'audit/grc-04-compliance.png', fullPage: true });

    // Check Controls link
    await page.click('text=Controls');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'audit/grc-05-controls.png', fullPage: true });

    // Check Policies link (new GRC page)
    await page.click('text=Policies');
    await page.waitForLoadState('networkidle');
    const policiesTitle = page.locator('h1:has-text("Policy Management")');
    await expect(policiesTitle).toBeVisible();
    await page.screenshot({ path: 'audit/grc-06-policies.png', fullPage: true });
  });

  test('Audit navigation works', async ({ page }) => {
    // Check Audit Planning link (new GRC page)
    await page.click('text=Audit Planning');
    await page.waitForLoadState('networkidle');
    const auditsTitle = page.locator('h1:has-text("Audit Management")');
    await expect(auditsTitle).toBeVisible();
    await page.screenshot({ path: 'audit/grc-07-audits.png', fullPage: true });

    // Check Findings link (new GRC page)
    await page.click('text=Findings');
    await page.waitForLoadState('networkidle');
    const findingsTitle = page.locator('h1:has-text("Findings")');
    await expect(findingsTitle).toBeVisible();
    await page.screenshot({ path: 'audit/grc-08-findings.png', fullPage: true });

    // Check Incidents link (new GRC page)
    await page.click('text=Incidents');
    await page.waitForLoadState('networkidle');
    const incidentsTitle = page.locator('h1:has-text("Incident Management")');
    await expect(incidentsTitle).toBeVisible();
    await page.screenshot({ path: 'audit/grc-09-incidents.png', fullPage: true });
  });

  test('Third Party navigation works', async ({ page }) => {
    // Check Vendor Register link (new GRC page)
    await page.click('text=Vendor Register');
    await page.waitForLoadState('networkidle');
    const vendorTitle = page.locator('h1:has-text("Vendor Risk Management")');
    await expect(vendorTitle).toBeVisible();
    await page.screenshot({ path: 'audit/grc-10-vendors.png', fullPage: true });

    // Check Evidence Library link (new GRC page)
    await page.click('text=Evidence Library');
    await page.waitForLoadState('networkidle');
    const evidenceTitle = page.locator('h1:has-text("Evidence Library")');
    await expect(evidenceTitle).toBeVisible();
    await page.screenshot({ path: 'audit/grc-11-evidence.png', fullPage: true });
  });

  test('Landing page has GRC branding', async ({ page }) => {
    // Go to landing page (logout first)
    await page.goto(`${BASE_URL}/welcome`);
    await page.waitForLoadState('networkidle');

    // Check for GRC branding in hero section (use first() to avoid strict mode violation)
    const heroTitle = page.locator('text=Governance, Risk & Compliance').first();
    await expect(heroTitle).toBeVisible();

    // Check for GRC modules section
    const modulesSection = page.locator('text=Six Integrated Modules');
    await expect(modulesSection).toBeVisible();

    await page.screenshot({ path: 'audit/grc-00-landing.png', fullPage: true });
  });
});
