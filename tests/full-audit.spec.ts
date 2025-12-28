import { test, expect } from '@playwright/test';

const BASE_URL = 'https://cortex.alexandratechlab.com';

test.setTimeout(180000); // 3 minutes

test.describe('Complete Application Audit', () => {
  test('Capture all pages and sub-pages', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });

    // Helper to close any modals
    const closeModals = async () => {
      try {
        const closeBtn = page.locator('button:has-text("Skip"), button:has-text("Close"), button:has-text("Cancel"), [aria-label="Close"]').first();
        if (await closeBtn.isVisible({ timeout: 1000 })) {
          await closeBtn.click();
          await page.waitForTimeout(500);
        }
      } catch (e) {}
      // Also try clicking overlay to close
      try {
        const overlay = page.locator('.fixed.inset-0.bg-black, .fixed.inset-0.bg-opacity');
        if (await overlay.isVisible({ timeout: 500 })) {
          await page.keyboard.press('Escape');
          await page.waitForTimeout(500);
        }
      } catch (e) {}
    };

    // Login first
    console.log('🔐 Logging in...');
    await page.goto(`${BASE_URL}/login`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'audit/01-login.png', fullPage: true });

    await page.fill('input[name="tenant"], input#tenant', 'default');
    await page.fill('input[name="email"], input#email', 'admin@cortex.io');
    await page.fill('input[name="password"], input#password', 'Admin123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard', { timeout: 15000 });
    await page.waitForLoadState('networkidle');

    // 1. Dashboard
    console.log('📸 1. Dashboard');
    await page.waitForTimeout(2000);
    await closeModals();
    await page.screenshot({ path: 'audit/02-dashboard.png', fullPage: true });

    // 2. Entities
    console.log('📸 2. Entities');
    await page.goto(`${BASE_URL}/entities`);
    await page.waitForLoadState('networkidle');
    await closeModals();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'audit/03-entities.png', fullPage: true });

    // 2b. Entity Detail
    console.log('📸 2b. Entity Detail');
    await page.goto(`${BASE_URL}/entities`);
    await page.waitForLoadState('networkidle');
    await closeModals();
    const entityLink = page.locator('a[href^="/entities/"]').first();
    if (await entityLink.isVisible({ timeout: 2000 })) {
      await entityLink.click();
      await page.waitForLoadState('networkidle');
      await closeModals();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'audit/04-entity-detail.png', fullPage: true });
    }

    // 3. Constraints
    console.log('📸 3. Constraints');
    await page.goto(`${BASE_URL}/constraints`);
    await page.waitForLoadState('networkidle');
    await closeModals();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'audit/05-constraints.png', fullPage: true });

    // 3b. Constraint Detail
    console.log('📸 3b. Constraint Detail');
    const constraintLink = page.locator('a[href^="/constraints/"]').first();
    if (await constraintLink.isVisible({ timeout: 2000 })) {
      await constraintLink.click();
      await page.waitForLoadState('networkidle');
      await closeModals();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'audit/06-constraint-detail.png', fullPage: true });
    }

    // 4. Dependencies
    console.log('📸 4. Dependencies');
    await page.goto(`${BASE_URL}/dependencies`);
    await page.waitForLoadState('networkidle');
    await closeModals();
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'audit/07-dependencies.png', fullPage: true });

    // 5. Risks
    console.log('📸 5. Risks');
    await page.goto(`${BASE_URL}/risks`);
    await page.waitForLoadState('networkidle');
    await closeModals();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: 'audit/08-risks.png', fullPage: true });

    // 5b. Test Recalculate button
    console.log('📸 5b. Risks - Recalculate Button');
    const recalcBtn = page.locator('button:has-text("Recalculate")');
    if (await recalcBtn.isVisible({ timeout: 2000 })) {
      await recalcBtn.click();
      await page.waitForTimeout(2000);
      await page.screenshot({ path: 'audit/09-risks-recalculating.png', fullPage: true });
    }

    // 6. Scenarios
    console.log('📸 6. Scenarios');
    await page.goto(`${BASE_URL}/scenarios`);
    await page.waitForLoadState('networkidle');
    await closeModals();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'audit/10-scenarios.png', fullPage: true });

    // 7. Audit Log
    console.log('📸 7. Audit Log');
    await page.goto(`${BASE_URL}/audit`);
    await page.waitForLoadState('networkidle');
    await closeModals();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'audit/11-audit-log.png', fullPage: true });

    // 8. Compliance Dashboard
    console.log('📸 8. Compliance Dashboard');
    await page.goto(`${BASE_URL}/compliance`);
    await page.waitForLoadState('networkidle');
    await closeModals();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: 'audit/12-compliance.png', fullPage: true });

    // 8b. Test Frameworks button
    const frameworksBtn = page.locator('button:has-text("Frameworks")');
    if (await frameworksBtn.isVisible({ timeout: 2000 })) {
      await frameworksBtn.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'audit/13-compliance-frameworks.png', fullPage: true });
    }

    // 8c. Test Controls button
    const controlsBtn = page.locator('button:has-text("Controls")');
    if (await controlsBtn.isVisible({ timeout: 2000 })) {
      await controlsBtn.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'audit/14-compliance-controls.png', fullPage: true });
    }

    // 9. Dependency Layers
    console.log('📸 9. Dependency Layers');
    await page.goto(`${BASE_URL}/dependency-layers`);
    await page.waitForLoadState('networkidle');
    await closeModals();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'audit/15-dependency-layers.png', fullPage: true });

    // 10. Cross-Layer Analysis
    console.log('📸 10. Cross-Layer Analysis');
    await page.goto(`${BASE_URL}/cross-layer`);
    await page.waitForLoadState('networkidle');
    await closeModals();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'audit/16-cross-layer.png', fullPage: true });

    // 11. Scenario Chains
    console.log('📸 11. Scenario Chains');
    await page.goto(`${BASE_URL}/scenario-chains`);
    await page.waitForLoadState('networkidle');
    await closeModals();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'audit/17-scenario-chains.png', fullPage: true });

    // 11b. Test New Chain button
    const newChainBtn = page.locator('button:has-text("New Chain")');
    if (await newChainBtn.isVisible({ timeout: 2000 })) {
      await newChainBtn.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'audit/18-scenario-chain-modal.png', fullPage: true });
      await closeModals();
    }

    // 12. Risk Justification
    console.log('📸 12. Risk Justification');
    await page.goto(`${BASE_URL}/risk-justification`);
    await page.waitForLoadState('networkidle');
    await closeModals();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'audit/19-risk-justification.png', fullPage: true });

    // 13. Institutional Memory
    console.log('📸 13. Institutional Memory');
    await page.goto(`${BASE_URL}/history`);
    await page.waitForLoadState('networkidle');
    await closeModals();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'audit/20-institutional-memory.png', fullPage: true });

    // Test tabs
    const timelineTab = page.locator('button:has-text("Entity Timeline")');
    if (await timelineTab.isVisible({ timeout: 2000 })) {
      await timelineTab.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'audit/21-memory-timeline.png', fullPage: true });
    }

    const changesTab = page.locator('button:has-text("Constraint Changes")');
    if (await changesTab.isVisible({ timeout: 2000 })) {
      await changesTab.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'audit/22-memory-changes.png', fullPage: true });
    }

    // 14. AI Analysis
    console.log('📸 14. AI Analysis');
    await page.goto(`${BASE_URL}/ai-analysis`);
    await page.waitForLoadState('networkidle');
    await closeModals();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'audit/23-ai-analysis.png', fullPage: true });

    // Test tabs
    const anomaliesTab = page.locator('button:has-text("Pending Anomalies")');
    if (await anomaliesTab.isVisible({ timeout: 2000 })) {
      await anomaliesTab.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'audit/24-ai-anomalies.png', fullPage: true });
    }

    const modelCardsTab = page.locator('button:has-text("Model Cards")');
    if (await modelCardsTab.isVisible({ timeout: 2000 })) {
      await modelCardsTab.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'audit/25-ai-model-cards.png', fullPage: true });
    }

    // Test Request Analysis button
    const requestAnalysisBtn = page.locator('button:has-text("Request Analysis")');
    if (await requestAnalysisBtn.isVisible({ timeout: 2000 })) {
      await requestAnalysisBtn.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'audit/26-ai-request-modal.png', fullPage: true });
      await closeModals();
    }

    // 15. Monitoring
    console.log('📸 15. Monitoring');
    await page.goto(`${BASE_URL}/monitoring`);
    await page.waitForLoadState('networkidle');
    await closeModals();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'audit/27-monitoring.png', fullPage: true });

    // Test Refresh button
    const refreshBtn = page.locator('button:has-text("Refresh")');
    if (await refreshBtn.isVisible({ timeout: 2000 })) {
      await refreshBtn.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'audit/28-monitoring-refresh.png', fullPage: true });
    }

    // 16. Simulations
    console.log('📸 16. Simulations');
    await page.goto(`${BASE_URL}/simulations`);
    await page.waitForLoadState('networkidle');
    await closeModals();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'audit/29-simulations.png', fullPage: true });

    // Test simulation types
    const monteCarlo = page.locator('text=Monte Carlo').first();
    if (await monteCarlo.isVisible({ timeout: 2000 })) {
      await monteCarlo.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'audit/30-sim-montecarlo.png', fullPage: true });
    }

    const cascadeAnalysis = page.locator('text=Cascade Analysis').first();
    if (await cascadeAnalysis.isVisible({ timeout: 2000 })) {
      await cascadeAnalysis.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'audit/31-sim-cascade.png', fullPage: true });
    }

    // 17. Analytics Dashboard
    console.log('📸 17. Analytics Dashboard');
    await page.goto(`${BASE_URL}/analytics`);
    await page.waitForLoadState('networkidle');
    await closeModals();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: 'audit/32-analytics.png', fullPage: true });

    // 18. User Management
    console.log('📸 18. User Management');
    await page.goto(`${BASE_URL}/admin/users`);
    await page.waitForLoadState('networkidle');
    await closeModals();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'audit/33-user-management.png', fullPage: true });

    // Test Add User button
    const addUserBtn = page.locator('button:has-text("Add User")');
    if (await addUserBtn.isVisible({ timeout: 2000 })) {
      await addUserBtn.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'audit/34-add-user-modal.png', fullPage: true });
      await closeModals();
    }

    // 19. Bulk Operations
    console.log('📸 19. Bulk Operations');
    await page.goto(`${BASE_URL}/bulk-operations`);
    await page.waitForLoadState('networkidle');
    await closeModals();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'audit/35-bulk-operations.png', fullPage: true });

    // 20. Settings
    console.log('📸 20. Settings');
    await page.goto(`${BASE_URL}/settings`);
    await page.waitForLoadState('networkidle');
    await closeModals();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'audit/36-settings.png', fullPage: true });

    // 21. Profile
    console.log('📸 21. Profile');
    await page.goto(`${BASE_URL}/profile`);
    await page.waitForLoadState('networkidle');
    await closeModals();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'audit/37-profile.png', fullPage: true });

    // 22. Security
    console.log('📸 22. Security');
    await page.goto(`${BASE_URL}/security`);
    await page.waitForLoadState('networkidle');
    await closeModals();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'audit/38-security.png', fullPage: true });

    // Test 2FA button
    const enable2FABtn = page.locator('button:has-text("Enable Two-Factor")');
    if (await enable2FABtn.isVisible({ timeout: 2000 })) {
      await enable2FABtn.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'audit/39-2fa-modal.png', fullPage: true });
      await closeModals();
    }

    // 23. Add Entity Modal
    console.log('📸 23. Add Entity Modal');
    await page.goto(`${BASE_URL}/entities`);
    await page.waitForLoadState('networkidle');
    await closeModals();
    const addEntityBtn = page.locator('button:has-text("Add Entity")');
    if (await addEntityBtn.isVisible({ timeout: 2000 })) {
      await addEntityBtn.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'audit/40-add-entity-modal.png', fullPage: true });
      await closeModals();
    }

    // 24. Add Constraint Modal
    console.log('📸 24. Add Constraint Modal');
    await page.goto(`${BASE_URL}/constraints`);
    await page.waitForLoadState('networkidle');
    await closeModals();
    const addConstraintBtn = page.locator('button:has-text("Add Constraint")');
    if (await addConstraintBtn.isVisible({ timeout: 2000 })) {
      await addConstraintBtn.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'audit/41-add-constraint-modal.png', fullPage: true });
      await closeModals();
    }

    // 25. Add Dependency Modal
    console.log('📸 25. Add Dependency Modal');
    await page.goto(`${BASE_URL}/dependencies`);
    await page.waitForLoadState('networkidle');
    await closeModals();
    const addDepBtn = page.locator('button:has-text("Add Dependency")');
    if (await addDepBtn.isVisible({ timeout: 2000 })) {
      await addDepBtn.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'audit/42-add-dependency-modal.png', fullPage: true });
      await closeModals();
    }

    console.log('✅ Full audit complete!');
  });
});
