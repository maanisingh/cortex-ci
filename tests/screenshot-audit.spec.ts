import { test, expect } from '@playwright/test';

const BASE_URL = 'https://cortex.alexandratechlab.com';

test.describe('Full Application Screenshot Audit', () => {
  test('Capture all pages', async ({ page }) => {
    // Set viewport for consistent screenshots
    await page.setViewportSize({ width: 1920, height: 1080 });

    // 1. Landing Page (before login)
    console.log('📸 Capturing Landing Page...');
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'screenshots/01-landing-page.png', fullPage: true });

    // 2. Login Page
    console.log('📸 Capturing Login Page...');
    await page.goto(`${BASE_URL}/login`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'screenshots/02-login-page.png', fullPage: true });

    // 3. Perform Login
    console.log('🔐 Logging in...');
    await page.fill('input[name="tenant"], input#tenant', 'default');
    await page.fill('input[name="email"], input#email', 'admin@cortex.io');
    await page.fill('input[name="password"], input#password', 'Admin123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    await page.waitForLoadState('networkidle');

    // 4. Dashboard
    console.log('📸 Capturing Dashboard...');
    await page.waitForTimeout(2000); // Wait for charts to load
    await page.screenshot({ path: 'screenshots/03-dashboard.png', fullPage: true });

    // 5. Entities Page
    console.log('📸 Capturing Entities Page...');
    await page.goto(`${BASE_URL}/entities`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'screenshots/04-entities.png', fullPage: true });

    // 6. Constraints Page
    console.log('📸 Capturing Constraints Page...');
    await page.goto(`${BASE_URL}/constraints`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'screenshots/05-constraints.png', fullPage: true });

    // 7. Dependencies Page
    console.log('📸 Capturing Dependencies Page...');
    await page.goto(`${BASE_URL}/dependencies`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'screenshots/06-dependencies.png', fullPage: true });

    // 8. Risks Page
    console.log('📸 Capturing Risks Page...');
    await page.goto(`${BASE_URL}/risks`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'screenshots/07-risks.png', fullPage: true });

    // 9. Scenarios Page
    console.log('📸 Capturing Scenarios Page...');
    await page.goto(`${BASE_URL}/scenarios`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'screenshots/08-scenarios.png', fullPage: true });

    // 10. Audit Log Page
    console.log('📸 Capturing Audit Log Page...');
    await page.goto(`${BASE_URL}/audit`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'screenshots/09-audit-log.png', fullPage: true });

    // 11. Compliance Dashboard
    console.log('📸 Capturing Compliance Dashboard...');
    await page.goto(`${BASE_URL}/compliance`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'screenshots/10-compliance.png', fullPage: true });

    // 12. Settings Page
    console.log('📸 Capturing Settings Page...');
    await page.goto(`${BASE_URL}/settings`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'screenshots/11-settings.png', fullPage: true });

    // 13. Profile Page
    console.log('📸 Capturing Profile Page...');
    await page.goto(`${BASE_URL}/profile`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'screenshots/12-profile.png', fullPage: true });

    // 14. Scenario Chains Page
    console.log('📸 Capturing Scenario Chains Page...');
    await page.goto(`${BASE_URL}/scenario-chains`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'screenshots/13-scenario-chains.png', fullPage: true });

    // 15. Risk Justification Page
    console.log('📸 Capturing Risk Justification Page...');
    await page.goto(`${BASE_URL}/risk-justification`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'screenshots/14-risk-justification.png', fullPage: true });

    // 16. History Page
    console.log('📸 Capturing History Page...');
    await page.goto(`${BASE_URL}/history`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'screenshots/15-history.png', fullPage: true });

    // 17. AI Analysis Page
    console.log('📸 Capturing AI Analysis Page...');
    await page.goto(`${BASE_URL}/ai-analysis`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'screenshots/16-ai-analysis.png', fullPage: true });

    // 18. Monitoring Page
    console.log('📸 Capturing Monitoring Page...');
    await page.goto(`${BASE_URL}/monitoring`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'screenshots/17-monitoring.png', fullPage: true });

    // 19. Dependency Layers Page
    console.log('📸 Capturing Dependency Layers Page...');
    await page.goto(`${BASE_URL}/dependency-layers`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'screenshots/18-dependency-layers.png', fullPage: true });

    // 20. Simulations Page
    console.log('📸 Capturing Simulations Page...');
    await page.goto(`${BASE_URL}/simulations`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'screenshots/19-simulations.png', fullPage: true });

    // 21. Analytics Dashboard
    console.log('📸 Capturing Analytics Dashboard...');
    await page.goto(`${BASE_URL}/analytics`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'screenshots/20-analytics.png', fullPage: true });

    // 22. Security Settings Page
    console.log('📸 Capturing Security Settings Page...');
    await page.goto(`${BASE_URL}/security`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'screenshots/21-security.png', fullPage: true });

    // 23. User Management Page (Admin)
    console.log('📸 Capturing User Management Page...');
    await page.goto(`${BASE_URL}/admin/users`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'screenshots/22-user-management.png', fullPage: true });

    // 24. Bulk Operations Page
    console.log('📸 Capturing Bulk Operations Page...');
    await page.goto(`${BASE_URL}/bulk-operations`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'screenshots/23-bulk-operations.png', fullPage: true });

    console.log('✅ All screenshots captured!');
  });
});
