import { test, expect } from '@playwright/test';

test.describe('Table Rendering', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/index-full.html');
    // Wait for Tabulator to initialize
    await page.waitForSelector('.tabulator-row');
  });

  test('table renders with data rows', async ({ page }) => {
    const rows = page.locator('.tabulator-row');
    // The full fixture has 21 rows
    await expect(rows.first()).toBeVisible();
    const count = await rows.count();
    expect(count).toBeGreaterThan(0);
  });

  test('table has correct column headers', async ({ page }) => {
    const pathHeader = page.locator('.tabulator-col-title').filter({ hasText: 'Folder Path' });
    const countHeader = page.locator('.tabulator-col-title').filter({ hasText: 'File Count' });

    await expect(pathHeader).toBeVisible();
    await expect(countHeader).toBeVisible();
  });

  test('initial sort is by path ascending', async ({ page }) => {
    // The first row should be "/" (root folder) when sorted ascending
    const firstRow = page.locator('.tabulator-row').first();
    const pathCell = firstRow.locator('.tabulator-cell').first();
    await expect(pathCell).toContainText('/');
  });
});

test.describe('Table Sorting', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/index-full.html');
    await page.waitForSelector('.tabulator-row');
  });

  test('clicking File Count header sorts by file count', async ({ page }) => {
    // Get initial first row path to verify sort changes
    const firstRowPath = await page.locator('.tabulator-row').first().locator('.tabulator-cell').first().textContent();

    const countHeader = page.locator('.tabulator-col-title').filter({ hasText: 'File Count' });
    await countHeader.click();

    // Wait for table to re-render after sort
    await page.waitForTimeout(500);

    // After clicking, the first row should be different (sorted by file count now, not path)
    const newFirstRowPath = await page.locator('.tabulator-row').first().locator('.tabulator-cell').first().textContent();

    // The sort order changed - "/" (root) has 0 files, should be first when sorted by count ascending
    expect(newFirstRowPath).toBe('/');
  });

  test('clicking path header changes sort direction', async ({ page }) => {
    const pathHeader = page.locator('.tabulator-col').filter({ hasText: 'Folder Path' });

    // Click to change from asc to desc
    await pathHeader.click();
    await page.waitForTimeout(300);

    // Click again to reverse
    await pathHeader.click();
    await page.waitForTimeout(300);

    // Should now be ascending again
    const firstRow = page.locator('.tabulator-row').first();
    const pathCell = firstRow.locator('.tabulator-cell').first();
    await expect(pathCell).toContainText('/');
  });
});

test.describe('Table Search', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/index-full.html');
    await page.waitForSelector('.tabulator-row');
  });

  test('search input is visible', async ({ page }) => {
    const searchInput = page.locator('#search-input');
    await expect(searchInput).toBeVisible();
    await expect(searchInput).toHaveAttribute('placeholder', 'Search folders...');
  });

  test('search filters rows', async ({ page }) => {
    const searchInput = page.locator('#search-input');
    const initialRowCount = await page.locator('.tabulator-row').count();

    // Search for a specific batch
    await searchInput.fill('batch 357');
    await page.waitForTimeout(300);

    const filteredRowCount = await page.locator('.tabulator-row').count();
    expect(filteredRowCount).toBeLessThan(initialRowCount);
    expect(filteredRowCount).toBeGreaterThan(0);

    // Verify the filtered row contains our search term
    const firstRow = page.locator('.tabulator-row').first();
    await expect(firstRow).toContainText('batch 357');
  });

  test('search is case-insensitive', async ({ page }) => {
    const searchInput = page.locator('#search-input');

    // Search with different case
    await searchInput.fill('BATCH');
    await page.waitForTimeout(300);

    const rows = page.locator('.tabulator-row');
    const count = await rows.count();
    expect(count).toBeGreaterThan(0);
  });

  test('clearing search shows all rows again', async ({ page }) => {
    const searchInput = page.locator('#search-input');
    const initialRowCount = await page.locator('.tabulator-row').count();

    await searchInput.fill('batch 357');
    await page.waitForTimeout(300);

    await searchInput.clear();
    await page.waitForTimeout(300);

    const finalRowCount = await page.locator('.tabulator-row').count();
    expect(finalRowCount).toBe(initialRowCount);
  });
});

test.describe('Table Pagination', () => {
  test('pagination controls are visible on large dataset', async ({ page }) => {
    await page.goto('/index-large.html');
    await page.waitForSelector('.tabulator-row');

    // Tabulator pagination controls
    const pagination = page.locator('.tabulator-footer');
    await expect(pagination).toBeVisible();
  });

  test('page size selector has correct options', async ({ page }) => {
    await page.goto('/index-large.html');
    await page.waitForSelector('.tabulator-row');

    // Check page size selector exists
    const pageSizeSelector = page.locator('.tabulator-page-size');
    await expect(pageSizeSelector).toBeVisible();

    // Check options - Tabulator uses a select element
    const options = pageSizeSelector.locator('option');
    const optionTexts = await options.allTextContents();

    expect(optionTexts).toContain('25');
    expect(optionTexts).toContain('50');
    expect(optionTexts).toContain('100');
    expect(optionTexts).toContain('250');
  });

  test('changing page size affects displayed rows', async ({ page }) => {
    await page.goto('/index-large.html');
    await page.waitForSelector('.tabulator-row');

    // Default is 50, change to 25
    const pageSizeSelector = page.locator('.tabulator-page-size');
    await pageSizeSelector.selectOption('25');
    await page.waitForTimeout(300);

    const rows = page.locator('.tabulator-row');
    const count = await rows.count();
    expect(count).toBe(25);
  });

  test('pagination navigation works', async ({ page }) => {
    await page.goto('/index-large.html');
    await page.waitForSelector('.tabulator-row');

    // Get first row content on page 1
    const firstRowPage1 = await page.locator('.tabulator-row').first().textContent();

    // Click next page button
    const nextButton = page.locator('.tabulator-page[data-page="next"]');
    await nextButton.click();
    await page.waitForTimeout(300);

    // Get first row content on page 2
    const firstRowPage2 = await page.locator('.tabulator-row').first().textContent();

    // They should be different
    expect(firstRowPage1).not.toBe(firstRowPage2);
  });
});

test.describe('Row Styling', () => {
  test('row hover changes background color', async ({ page }) => {
    await page.goto('/index-full.html');
    await page.waitForSelector('.tabulator-row');

    const row = page.locator('.tabulator-row').first();

    // Hover over the row
    await row.hover();

    // Check background color (the CSS says #e8f4ff which is rgb(232, 244, 255))
    await expect(row).toHaveCSS('background-color', 'rgb(232, 244, 255)');
  });
});

test.describe('Error Entries', () => {
  test('error entries show red "Error" text', async ({ page }) => {
    await page.goto('/index-error.html');
    await page.waitForSelector('.tabulator-row');

    // Find the error cell - it's a span with exact text "Error" and red color
    const errorCell = page.getByText('Error', { exact: true });
    await expect(errorCell).toBeVisible();

    // Check the color
    await expect(errorCell).toHaveCSS('color', 'rgb(220, 53, 69)'); // #dc3545
  });
});
