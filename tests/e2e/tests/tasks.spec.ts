import { test, expect } from '@playwright/test';

test.describe('Task Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"], input[name="email"]', 'demo@cortex.local');
    await page.fill('input[type="password"], input[name="password"]', 'demo123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/dashboard/);
  });

  test('should display compliance tasks list', async ({ page }) => {
    await page.goto('/compliance-tasks');
    await expect(page.locator('h1, h2')).toContainText(/задач|task/i);
  });

  test('should show kanban board view', async ({ page }) => {
    await page.goto('/compliance-tasks');

    // Switch to kanban view
    await page.click('button:has-text("Kanban"), button:has-text("Доска")');

    // Check for kanban columns
    await expect(page.locator('text=/к выполнению|to do|в работе|in progress/i')).toBeVisible();
  });

  test('should display calendar view', async ({ page }) => {
    await page.goto('/compliance-calendar');

    // Check for calendar elements
    await expect(page.locator('text=/календарь|calendar/i')).toBeVisible();
    await expect(page.locator('[class*="calendar"], [role="grid"]')).toBeVisible();
  });

  test('should create new task', async ({ page }) => {
    await page.goto('/compliance-tasks');

    // Click create button
    await page.click('button:has-text("Создать"), button:has-text("Create"), button:has-text("+")');

    // Fill task form
    await page.fill('input[name="title"], input[placeholder*="название"]', 'Тестовая задача');
    await page.fill('textarea[name="description"]', 'Описание тестовой задачи');

    // Save
    await page.click('button:has-text("Сохранить"), button:has-text("Save")');

    // Should see new task
    await expect(page.locator('text="Тестовая задача"')).toBeVisible();
  });

  test('should filter tasks by status', async ({ page }) => {
    await page.goto('/compliance-tasks');

    // Apply filter
    await page.click('button:has-text("Фильтр"), button:has-text("Filter")');
    await page.click('text=/в работе|in progress/i');

    // Results should be filtered
    await expect(page.locator('text=/в работе|in progress/i')).toBeVisible();
  });

  test('should show task details', async ({ page }) => {
    await page.goto('/compliance-tasks');

    // Click on a task
    await page.click('tr, div[class*="task"]').first();

    // Details should appear
    await expect(page.locator('text=/описание|description|срок|deadline/i')).toBeVisible();
  });

  test('should mark task as complete', async ({ page }) => {
    await page.goto('/compliance-tasks');

    // Find and click complete checkbox
    await page.click('input[type="checkbox"], button:has-text("Выполнено")').first();

    // Task status should update
    await expect(page.locator('text=/выполнен|completed|done/i')).toBeVisible();
  });
});
