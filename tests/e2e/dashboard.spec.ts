import { test, expect } from '@playwright/test';

test.describe('Dashboard Layout', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/index-full.html');
  });

  test('has correct page title', async ({ page }) => {
    await expect(page).toHaveTitle('Dropbox Folder File Count Report');
  });

  test('displays header h1 with correct text and color', async ({ page }) => {
    const header = page.locator('h1');
    await expect(header).toHaveText('Dropbox Folder File Count Report');
    await expect(header).toHaveCSS('color', 'rgb(0, 97, 254)'); // #0061fe
  });

  test('displays timestamp in meta-info with UTC format', async ({ page }) => {
    const metaInfo = page.locator('.meta-info');
    await expect(metaInfo).toBeVisible();
    await expect(metaInfo).toContainText('Generated:');
    await expect(metaInfo).toContainText('UTC');
  });

  test('displays stats panel with Total Folders', async ({ page }) => {
    const statBoxes = page.locator('.stat-box');
    const totalFoldersBox = statBoxes.filter({ hasText: 'Total Folders' });
    await expect(totalFoldersBox).toBeVisible();

    const value = totalFoldersBox.locator('.value');
    await expect(value).toHaveText('21');
  });

  test('displays stats panel with Total Files formatted with commas', async ({ page }) => {
    const statBoxes = page.locator('.stat-box');
    const totalFilesBox = statBoxes.filter({ hasText: 'Total Files' });
    await expect(totalFilesBox).toBeVisible();

    const value = totalFilesBox.locator('.value');
    await expect(value).toHaveText('36,318');
  });

  test('displays footer', async ({ page }) => {
    const footer = page.locator('.footer');
    await expect(footer).toBeVisible();
    await expect(footer).toContainText('Report generated automatically');
  });
});

test.describe('Change Indicator Colors', () => {
  test('shows red color for increase (full fixture)', async ({ page }) => {
    await page.goto('/index-full.html');
    const changeBox = page.locator('.stat-box.change-box .value');
    await expect(changeBox).toHaveCSS('color', 'rgb(220, 53, 69)'); // #dc3545
  });

  test('shows green color for decrease (error fixture)', async ({ page }) => {
    await page.goto('/index-error.html');
    const changeBox = page.locator('.stat-box.change-box .value');
    await expect(changeBox).toHaveCSS('color', 'rgb(40, 167, 69)'); // #28a745
  });

  test('shows neutral color for no change (empty fixture)', async ({ page }) => {
    await page.goto('/index-empty.html');
    const changeBox = page.locator('.stat-box.change-box .value');
    await expect(changeBox).toHaveCSS('color', 'rgb(102, 102, 102)'); // #666
  });

  test('shows neutral color for no change (no-history fixture)', async ({ page }) => {
    await page.goto('/index-no-history.html');
    const changeBox = page.locator('.stat-box.change-box .value');
    await expect(changeBox).toHaveCSS('color', 'rgb(102, 102, 102)'); // #666
  });
});

test.describe('Empty State', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/index-empty.html');
  });

  test('shows zero totals', async ({ page }) => {
    const statBoxes = page.locator('.stat-box');

    const foldersValue = statBoxes.filter({ hasText: 'Total Folders' }).locator('.value');
    await expect(foldersValue).toHaveText('0');

    const filesValue = statBoxes.filter({ hasText: 'Total Files' }).locator('.value');
    await expect(filesValue).toHaveText('0');
  });

  test('table renders but has no data rows', async ({ page }) => {
    const table = page.locator('#folder-table');
    await expect(table).toBeVisible();

    // Wait for Tabulator to initialize
    await page.waitForSelector('.tabulator-header');

    // Check that there are no data rows (only header)
    const rows = page.locator('.tabulator-row');
    await expect(rows).toHaveCount(0);
  });
});
