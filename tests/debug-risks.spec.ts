import { test, expect } from '@playwright/test';

const BASE_URL = 'https://cortex.alexandratechlab.com';

test('Debug Risks Page', async ({ page }) => {
  const consoleErrors: string[] = [];
  const networkErrors: string[] = [];

  // Capture console errors
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });

  // Capture failed requests
  page.on('requestfailed', request => {
    networkErrors.push(`${request.url()} - ${request.failure()?.errorText}`);
  });

  // Capture response errors
  page.on('response', response => {
    if (response.status() >= 400) {
      networkErrors.push(`${response.url()} - Status: ${response.status()}`);
    }
  });

  // Login first
  await page.goto(`${BASE_URL}/login`);
  await page.fill('input[name="tenant"], input#tenant', 'default');
  await page.fill('input[name="email"], input#email', 'admin@cortex.io');
  await page.fill('input[name="password"], input#password', 'Admin123!');
  await page.click('button[type="submit"]');
  await page.waitForURL('**/dashboard', { timeout: 10000 });

  // Navigate to Risks page
  console.log('Navigating to Risks page...');
  await page.goto(`${BASE_URL}/risks`);
  await page.waitForTimeout(5000); // Wait for any API calls

  // Check page content
  const pageContent = await page.content();
  console.log('Page title present:', pageContent.includes('Risk Assessment'));
  console.log('Table present:', pageContent.includes('table'));

  // Check for visible elements
  const hasHeader = await page.locator('h1:has-text("Risk")').count();
  console.log('Risk header found:', hasHeader);

  // Log errors
  console.log('\n=== Console Errors ===');
  consoleErrors.forEach(e => console.log(e));

  console.log('\n=== Network Errors ===');
  networkErrors.forEach(e => console.log(e));

  // Take screenshot
  await page.screenshot({ path: 'screenshots/debug-risks.png', fullPage: true });

  // Also check HTML structure
  const html = await page.evaluate(() => document.body.innerHTML);
  console.log('\n=== Body HTML (first 2000 chars) ===');
  console.log(html.substring(0, 2000));
});
