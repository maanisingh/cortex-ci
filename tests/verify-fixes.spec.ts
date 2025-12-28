import { test, expect } from '@playwright/test';

const BASE_URL = 'https://cortex.alexandratechlab.com';

test.setTimeout(120000);

test('Verify fixed pages', async ({ page }) => {
  await page.setViewportSize({ width: 1920, height: 1080 });

  // Login
  await page.goto(`${BASE_URL}/login`);
  await page.fill('input#tenant', 'default');
  await page.fill('input#email', 'admin@cortex.io');
  await page.fill('input#password', 'Admin123!');
  await page.click('button[type="submit"]');
  await page.waitForURL('**/dashboard', { timeout: 15000 });

  // Test Entity Detail
  console.log('Testing Entity Detail page...');
  await page.goto(`${BASE_URL}/entities`);
  await page.waitForLoadState('networkidle');

  const entityLink = page.locator('a[href^="/entities/"]').first();
  if (await entityLink.isVisible({ timeout: 3000 })) {
    await entityLink.click();
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'audit/verify-entity-detail.png', fullPage: true });

    const hasContent = await page.locator('h1, text=Entity').count();
    console.log('Entity Detail has content:', hasContent > 0);
  }

  // Test Cross-Layer Analysis
  console.log('Testing Cross-Layer Analysis page...');
  await page.goto(`${BASE_URL}/cross-layer`);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(2000);
  await page.screenshot({ path: 'audit/verify-cross-layer.png', fullPage: true });

  const hasCrossLayerContent = await page.locator('h1:has-text("Cross-Layer")').count();
  console.log('Cross-Layer Analysis has content:', hasCrossLayerContent > 0);

  // Test Risks page
  console.log('Testing Risks page...');
  await page.goto(`${BASE_URL}/risks`);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(2000);
  await page.screenshot({ path: 'audit/verify-risks.png', fullPage: true });

  const hasRisksContent = await page.locator('h1:has-text("Risk")').count();
  console.log('Risks page has content:', hasRisksContent > 0);

  console.log('✅ Verification complete!');
});
