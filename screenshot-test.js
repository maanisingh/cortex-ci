const { chromium } = require('playwright');

const BASE_URL = 'http://localhost:3002';

// Pages to screenshot
const publicPages = [
  { path: '/', name: 'landing' },
  { path: '/login', name: 'login' },
];

const protectedPages = [
  { path: '/dashboard', name: 'dashboard' },
  { path: '/entities', name: 'entities' },
  { path: '/constraints', name: 'constraints' },
  { path: '/risks', name: 'risks' },
  { path: '/scenarios', name: 'scenarios' },
  { path: '/compliance', name: 'compliance' },
  { path: '/policies', name: 'policies' },
  { path: '/vendors', name: 'vendors' },
  { path: '/russian-compliance', name: 'russian-compliance' },
  { path: '/analytics', name: 'analytics' },
  { path: '/settings', name: 'settings' },
];

const languages = ['ru', 'en', 'kk', 'uz', 'hy', 'ka', 'az'];

async function takeScreenshots() {
  const browser = await chromium.launch({ headless: true });

  for (const lang of languages) {
    console.log(`\n--- Taking screenshots for language: ${lang} ---`);
    const context = await browser.newContext({
      viewport: { width: 1920, height: 1080 },
    });

    const page = await context.newPage();

    // Navigate to base URL first
    await page.goto(BASE_URL, { waitUntil: 'networkidle', timeout: 15000 });

    // Set language in localStorage
    await page.evaluate((language) => {
      localStorage.setItem('cortex-language', language);
    }, lang);

    // Take screenshots of public pages
    for (const p of publicPages) {
      try {
        await page.goto(`${BASE_URL}${p.path}`, { waitUntil: 'networkidle', timeout: 15000 });
        await page.waitForTimeout(500);
        const filename = `/home/maani/cortex-ci/screenshots/${lang}_${p.name}.png`;
        await page.screenshot({ path: filename, fullPage: true });
        console.log(`Captured: ${filename}`);
      } catch (e) {
        console.log(`Failed to capture ${p.name}: ${e.message}`);
      }
    }

    // Set auth state in localStorage with correct structure for zustand persist
    await page.evaluate(() => {
      const authState = {
        state: {
          user: {
            id: '1',
            email: 'admin@cortex.com',
            full_name: 'Admin User',
            role: 'admin',
            tenant_id: 'tenant-1'
          },
          accessToken: 'mock-access-token-for-screenshots',
          refreshToken: 'mock-refresh-token',
          tenantId: 'tenant-1',
          isAuthenticated: true,
        },
        version: 0
      };
      localStorage.setItem('cortex-auth', JSON.stringify(authState));
    });

    // Take screenshots of protected pages
    for (const p of protectedPages) {
      try {
        await page.goto(`${BASE_URL}${p.path}`, { waitUntil: 'networkidle', timeout: 15000 });
        await page.waitForTimeout(800);
        const filename = `/home/maani/cortex-ci/screenshots/${lang}_${p.name}.png`;
        await page.screenshot({ path: filename, fullPage: true });
        console.log(`Captured: ${filename}`);
      } catch (e) {
        console.log(`Failed to capture ${p.name}: ${e.message}`);
      }
    }

    await context.close();
  }

  await browser.close();
  console.log('\n--- All screenshots completed ---');
}

takeScreenshots().catch(console.error);
