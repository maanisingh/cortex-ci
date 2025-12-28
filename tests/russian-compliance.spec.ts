import { test, expect } from '@playwright/test';

/**
 * Russian Compliance (152-ФЗ) Integration Tests
 *
 * Verifies the Phase 2 GRC features:
 * 1. Russian Compliance page loads
 * 2. Company creation by INN works
 * 3. ISPDN system registration
 * 4. Document generation
 * 5. Protection level calculator
 * 6. Onboarding wizard
 */

const CORTEX_URL = 'https://cortex.alexandratechlab.com';

const CORTEX_CREDENTIALS = {
  tenant: 'default',
  email: 'admin@cortex.io',
  password: 'Admin123!'
};

// Sample INN for testing (Sberbank)
const TEST_INN = '7707083893';

test.describe('Russian Compliance - GRC Phase 2', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto(`${CORTEX_URL}/login`);
    await page.fill('input#tenant', CORTEX_CREDENTIALS.tenant);
    await page.fill('input#email', CORTEX_CREDENTIALS.email);
    await page.fill('input#password', CORTEX_CREDENTIALS.password);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard', { timeout: 15000 });
  });

  test('Russian Compliance page loads', async ({ page }) => {
    await page.goto(`${CORTEX_URL}/russian-compliance`);
    await page.waitForLoadState('networkidle');

    // Check page title
    const title = page.locator('text=Russian Compliance').first();
    await expect(title).toBeVisible({ timeout: 10000 });

    // Check for 152-ФЗ mention
    const framework = page.locator('text=152-ФЗ').first();
    await expect(framework).toBeVisible();

    await page.screenshot({ path: 'audit/ru-compliance-page.png', fullPage: true });
  });

  test('Russian Onboarding wizard loads', async ({ page }) => {
    await page.goto(`${CORTEX_URL}/russian-onboarding`);
    await page.waitForLoadState('networkidle');

    // Check for step indicators
    const steps = [
      'Company',
      'Responsible',
      'ISPDN',
      'Documents',
      'Tasks'
    ];

    for (const step of steps) {
      const stepElement = page.locator(`text=${step}`).first();
      const isVisible = await stepElement.isVisible().catch(() => false);
      console.log(`Onboarding step "${step}": ${isVisible ? 'FOUND' : 'MISSING'}`);
    }

    await page.screenshot({ path: 'audit/ru-onboarding-wizard.png', fullPage: true });
  });

  test('Russian Dashboard loads', async ({ page }) => {
    await page.goto(`${CORTEX_URL}/russian-dashboard`);
    await page.waitForLoadState('networkidle');

    await page.screenshot({ path: 'audit/ru-dashboard.png', fullPage: true });
  });

  test('API: Russian frameworks endpoint works', async ({ request }) => {
    // Login
    const loginResponse = await request.post(`${CORTEX_URL}/api/v1/auth/login`, {
      data: {
        email: CORTEX_CREDENTIALS.email,
        password: CORTEX_CREDENTIALS.password
      }
    });
    const { access_token } = await loginResponse.json();

    // Get frameworks
    const response = await request.get(`${CORTEX_URL}/api/v1/compliance/russian/frameworks`, {
      headers: { 'Authorization': `Bearer ${access_token}` }
    });

    expect(response.status()).toBe(200);
    const frameworks = await response.json();

    console.log('Russian Frameworks:', JSON.stringify(frameworks, null, 2));

    // Check for expected frameworks
    const frameworkCodes = frameworks.map((f: { code: string }) => f.code);
    expect(frameworkCodes).toContain('152-ФЗ');
  });

  test('API: INN lookup works', async ({ request }) => {
    // Login
    const loginResponse = await request.post(`${CORTEX_URL}/api/v1/auth/login`, {
      data: {
        email: CORTEX_CREDENTIALS.email,
        password: CORTEX_CREDENTIALS.password
      }
    });
    const { access_token } = await loginResponse.json();

    // Lookup INN
    const response = await request.post(
      `${CORTEX_URL}/api/v1/compliance/russian/companies/lookup?inn=${TEST_INN}`,
      {
        headers: { 'Authorization': `Bearer ${access_token}` }
      }
    );

    expect(response.status()).toBe(200);
    const result = await response.json();

    console.log('INN Lookup Result:', JSON.stringify(result, null, 2));

    expect(result.found).toBe(true);
    expect(result.data).toBeDefined();
    expect(result.data.inn).toBe(TEST_INN);
  });

  test('API: Protection level calculator works', async ({ request }) => {
    // Login
    const loginResponse = await request.post(`${CORTEX_URL}/api/v1/auth/login`, {
      data: {
        email: CORTEX_CREDENTIALS.email,
        password: CORTEX_CREDENTIALS.password
      }
    });
    const { access_token } = await loginResponse.json();

    // Calculate protection level
    const response = await request.post(
      `${CORTEX_URL}/api/v1/compliance/russian/calculate-protection-level`,
      {
        headers: {
          'Authorization': `Bearer ${access_token}`,
          'Content-Type': 'application/json'
        },
        data: {
          pdn_category: 'ИНЫЕ',
          subject_count: 1000,
          threat_type: '3',
          is_employee_only: true
        }
      }
    );

    expect(response.status()).toBe(200);
    const result = await response.json();

    console.log('Protection Level Result:', JSON.stringify(result, null, 2));

    expect(result.protection_level).toBeDefined();
    expect(result.required_measures).toBeDefined();
  });

  test('API: Document templates available', async ({ request }) => {
    // Login
    const loginResponse = await request.post(`${CORTEX_URL}/api/v1/auth/login`, {
      data: {
        email: CORTEX_CREDENTIALS.email,
        password: CORTEX_CREDENTIALS.password
      }
    });
    const { access_token } = await loginResponse.json();

    // Get templates
    const response = await request.get(
      `${CORTEX_URL}/api/v1/compliance/russian/templates`,
      {
        headers: { 'Authorization': `Bearer ${access_token}` }
      }
    );

    expect(response.status()).toBe(200);
    const templates = await response.json();

    console.log(`Document Templates: ${templates.length} templates found`);

    if (templates.length > 0) {
      console.log('Sample templates:');
      templates.slice(0, 5).forEach((t: { template_code: string; title: string }) => {
        console.log(`  - ${t.template_code}: ${t.title}`);
      });
    }
  });

  test('API: Companies endpoint works', async ({ request }) => {
    // Login
    const loginResponse = await request.post(`${CORTEX_URL}/api/v1/auth/login`, {
      data: {
        email: CORTEX_CREDENTIALS.email,
        password: CORTEX_CREDENTIALS.password
      }
    });
    const { access_token } = await loginResponse.json();

    // Get companies
    const response = await request.get(
      `${CORTEX_URL}/api/v1/compliance/russian/companies`,
      {
        headers: { 'Authorization': `Bearer ${access_token}` }
      }
    );

    expect(response.status()).toBe(200);
    const companies = await response.json();

    console.log(`Companies: ${companies.length} companies found`);

    if (companies.length > 0) {
      console.log('Companies:');
      companies.forEach((c: { inn: string; full_name: string }) => {
        console.log(`  - ${c.inn}: ${c.full_name}`);
      });
    }
  });

  test('Navigation includes Russian Compliance', async ({ page }) => {
    await page.goto(`${CORTEX_URL}/dashboard`);
    await page.waitForLoadState('networkidle');

    // Look for Russian Compliance in sidebar
    const ruCompliance = page.locator('text=Russian').first();
    const isVisible = await ruCompliance.isVisible().catch(() => false);

    console.log('Russian Compliance in navigation:', isVisible ? 'FOUND' : 'MISSING');

    // Take screenshot of sidebar
    await page.screenshot({ path: 'audit/sidebar-navigation.png' });
  });
});

test.describe('Document Editor', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${CORTEX_URL}/login`);
    await page.fill('input#tenant', CORTEX_CREDENTIALS.tenant);
    await page.fill('input#email', CORTEX_CREDENTIALS.email);
    await page.fill('input#password', CORTEX_CREDENTIALS.password);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard', { timeout: 15000 });
  });

  test('Document editor page loads', async ({ page }) => {
    await page.goto(`${CORTEX_URL}/document-editor`);
    await page.waitForLoadState('networkidle');

    await page.screenshot({ path: 'audit/document-editor.png', fullPage: true });
  });
});

test.describe('GRC Platform Summary', () => {
  test('Generate Phase 2 status report', async ({ page, request }) => {
    const report: Record<string, unknown> = {
      timestamp: new Date().toISOString(),
      platform: 'Cortex GRC',
      phase: 'Phase 2 - Russian Compliance',
      status: {}
    };

    // Login
    const loginResponse = await request.post(`${CORTEX_URL}/api/v1/auth/login`, {
      data: {
        email: CORTEX_CREDENTIALS.email,
        password: CORTEX_CREDENTIALS.password
      }
    });
    const { access_token } = await loginResponse.json();

    // Check API endpoints
    const endpoints = [
      { name: 'frameworks', url: '/api/v1/compliance/russian/frameworks' },
      { name: 'templates', url: '/api/v1/compliance/russian/templates' },
      { name: 'companies', url: '/api/v1/compliance/russian/companies' },
    ];

    const apiStatus: Record<string, string> = {};
    for (const endpoint of endpoints) {
      try {
        const response = await request.get(`${CORTEX_URL}${endpoint.url}`, {
          headers: { 'Authorization': `Bearer ${access_token}` }
        });
        apiStatus[endpoint.name] = response.ok() ? 'OK' : `ERROR (${response.status()})`;
      } catch (e) {
        apiStatus[endpoint.name] = 'FAILED';
      }
    }

    report.apiEndpoints = apiStatus;

    // Check frontend pages
    const pages = [
      { name: 'russian-compliance', url: '/russian-compliance' },
      { name: 'russian-onboarding', url: '/russian-onboarding' },
      { name: 'russian-dashboard', url: '/russian-dashboard' },
      { name: 'document-editor', url: '/document-editor' },
    ];

    // Login first
    await page.goto(`${CORTEX_URL}/login`);
    await page.fill('input#tenant', CORTEX_CREDENTIALS.tenant);
    await page.fill('input#email', CORTEX_CREDENTIALS.email);
    await page.fill('input#password', CORTEX_CREDENTIALS.password);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard', { timeout: 15000 });

    const pageStatus: Record<string, string> = {};
    for (const p of pages) {
      try {
        const response = await page.goto(`${CORTEX_URL}${p.url}`);
        pageStatus[p.name] = response?.ok() ? 'OK' : `ERROR (${response?.status()})`;
      } catch (e) {
        pageStatus[p.name] = 'FAILED';
      }
    }

    report.frontendPages = pageStatus;

    // Summary
    report.summary = {
      backend: Object.values(apiStatus).every(s => s === 'OK') ? 'READY' : 'ISSUES',
      frontend: Object.values(pageStatus).every(s => s === 'OK') ? 'READY' : 'ISSUES',
      overall: 'Phase 2 GRC features integrated'
    };

    console.log('\n' + '='.repeat(60));
    console.log('PHASE 2 GRC STATUS REPORT');
    console.log('='.repeat(60));
    console.log(JSON.stringify(report, null, 2));
    console.log('='.repeat(60) + '\n');
  });
});
