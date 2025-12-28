const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const BASE_URL = 'http://localhost:3005';
const SCREENSHOT_DIR = path.join(__dirname, 'screenshots');

// All pages to screenshot
const pages = [
  { name: 'landing', path: '/', requiresAuth: false },
  { name: 'login', path: '/login', requiresAuth: false },
  { name: 'dashboard', path: '/dashboard', requiresAuth: true },
  { name: 'entities', path: '/entities', requiresAuth: true },
  { name: 'constraints', path: '/constraints', requiresAuth: true },
  { name: 'dependencies', path: '/dependencies', requiresAuth: true },
  { name: 'risks', path: '/risks', requiresAuth: true },
  { name: 'scenarios', path: '/scenarios', requiresAuth: true },
  { name: 'audit-log', path: '/audit', requiresAuth: true },
  { name: 'compliance', path: '/compliance', requiresAuth: true },
  { name: 'policies', path: '/policies', requiresAuth: true },
  { name: 'russian-compliance', path: '/russian-compliance', requiresAuth: true },
  { name: 'findings', path: '/findings', requiresAuth: true },
  { name: 'incidents', path: '/incidents', requiresAuth: true },
  { name: 'vendors', path: '/vendors', requiresAuth: true },
  { name: 'evidence', path: '/evidence', requiresAuth: true },
  { name: 'audits', path: '/audits', requiresAuth: true },
  { name: 'history', path: '/history', requiresAuth: true },
  { name: 'ai-analysis', path: '/ai-analysis', requiresAuth: true },
  { name: 'monitoring', path: '/monitoring', requiresAuth: true },
  { name: 'settings', path: '/settings', requiresAuth: true },
  { name: 'simulations', path: '/simulations', requiresAuth: true },
  { name: 'analytics', path: '/analytics', requiresAuth: true },
];

// Languages to test
const languages = [
  { code: 'ru', name: 'Russian' },
  { code: 'en', name: 'English' },
  { code: 'kk', name: 'Kazakh' },
  { code: 'uz', name: 'Uzbek' },
];

async function setLanguage(page, langCode) {
  // Set language in localStorage
  await page.evaluate((code) => {
    localStorage.setItem('cortex-language', code);
  }, langCode);
}

async function login(page) {
  await page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle0', timeout: 30000 });

  // Click demo account button if available
  try {
    await page.waitForSelector('button', { timeout: 5000 });
    const buttons = await page.$$('button');
    for (const btn of buttons) {
      const text = await page.evaluate(el => el.textContent, btn);
      if (text && text.includes('Demo')) {
        await btn.click();
        await page.waitForNavigation({ waitUntil: 'networkidle0', timeout: 10000 }).catch(() => {});
        return true;
      }
    }
  } catch (e) {
    console.log('Demo button not found, trying manual login');
  }

  // Try manual login
  try {
    await page.type('input[type="email"], input[name="email"]', 'admin@cortex.io');
    await page.type('input[type="password"], input[name="password"]', 'Admin123!');
    await page.click('button[type="submit"]');
    await page.waitForNavigation({ waitUntil: 'networkidle0', timeout: 10000 }).catch(() => {});
    return true;
  } catch (e) {
    console.log('Login failed:', e.message);
    return false;
  }
}

async function takeScreenshots() {
  // Create screenshot directory
  if (!fs.existsSync(SCREENSHOT_DIR)) {
    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  }

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
  });

  try {
    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });

    for (const lang of languages) {
      console.log(`\n=== Taking screenshots for ${lang.name} (${lang.code}) ===\n`);

      const langDir = path.join(SCREENSHOT_DIR, lang.code);
      if (!fs.existsSync(langDir)) {
        fs.mkdirSync(langDir, { recursive: true });
      }

      // Set language
      await page.goto(BASE_URL, { waitUntil: 'networkidle0', timeout: 30000 });
      await setLanguage(page, lang.code);
      await page.reload({ waitUntil: 'networkidle0' });

      let isLoggedIn = false;

      for (const pageInfo of pages) {
        try {
          if (pageInfo.requiresAuth && !isLoggedIn) {
            console.log('Logging in...');
            isLoggedIn = await login(page);
            if (!isLoggedIn) {
              console.log('Could not log in, skipping authenticated pages');
              continue;
            }
            // Re-set language after login
            await setLanguage(page, lang.code);
          }

          const url = `${BASE_URL}${pageInfo.path}`;
          console.log(`  Capturing: ${pageInfo.name} (${url})`);

          await page.goto(url, { waitUntil: 'networkidle0', timeout: 30000 });
          await new Promise(r => setTimeout(r, 1000)); // Wait for any animations

          const filename = `${pageInfo.name}.png`;
          await page.screenshot({
            path: path.join(langDir, filename),
            fullPage: true,
          });

          console.log(`    ✓ Saved: ${lang.code}/${filename}`);
        } catch (error) {
          console.log(`    ✗ Error on ${pageInfo.name}: ${error.message}`);
        }
      }
    }
  } finally {
    await browser.close();
  }

  console.log('\n=== Screenshots complete ===');
  console.log(`Screenshots saved to: ${SCREENSHOT_DIR}`);
}

takeScreenshots().catch(console.error);
