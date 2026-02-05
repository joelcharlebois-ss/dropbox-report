import { test, expect } from '@playwright/test';

test.describe('Chart Rendering', () => {
  test('chart canvas is present and visible with history data', async ({ page }) => {
    await page.goto('/index-full.html');

    const canvas = page.locator('#progressChart');
    await expect(canvas).toBeVisible();
  });

  test('chart container is visible', async ({ page }) => {
    await page.goto('/index-full.html');

    const chartContainer = page.locator('.chart-container');
    await expect(chartContainer).toBeVisible();
  });

  test('chart title displays "14-Day Progress"', async ({ page }) => {
    await page.goto('/index-full.html');

    const chartTitle = page.locator('.chart-title');
    await expect(chartTitle).toBeVisible();
    await expect(chartTitle).toHaveText('14-Day Progress');
  });

  test('Chart.js renders on canvas (canvas has dimensions)', async ({ page }) => {
    await page.goto('/index-full.html');

    // Wait for Chart.js to render
    await page.waitForTimeout(500);

    const canvas = page.locator('#progressChart');

    // Check that the canvas has been rendered with actual dimensions
    const boundingBox = await canvas.boundingBox();
    expect(boundingBox).not.toBeNull();
    expect(boundingBox!.width).toBeGreaterThan(0);
    expect(boundingBox!.height).toBeGreaterThan(0);
  });
});

test.describe('Chart Hidden States', () => {
  test('chart container is hidden when no history data', async ({ page }) => {
    await page.goto('/index-no-history.html');

    // The no-history fixture doesn't have the chart container
    const chartContainer = page.locator('.chart-container');
    await expect(chartContainer).not.toBeVisible();
  });

  test('chart canvas is not present when no history', async ({ page }) => {
    await page.goto('/index-no-history.html');

    const canvas = page.locator('#progressChart');
    await expect(canvas).toHaveCount(0);
  });

  test('chart is hidden in empty state', async ({ page }) => {
    await page.goto('/index-empty.html');

    // Empty fixture also doesn't have chart
    const chartContainer = page.locator('.chart-container');
    await expect(chartContainer).not.toBeVisible();
  });
});

test.describe('Chart with Different Data', () => {
  test('chart renders correctly on error page (has chart)', async ({ page }) => {
    await page.goto('/index-error.html');

    const canvas = page.locator('#progressChart');
    await expect(canvas).toBeVisible();

    // Wait for Chart.js to render
    await page.waitForTimeout(500);

    const boundingBox = await canvas.boundingBox();
    expect(boundingBox).not.toBeNull();
    expect(boundingBox!.width).toBeGreaterThan(0);
  });

  test('chart renders correctly on large dataset page', async ({ page }) => {
    await page.goto('/index-large.html');

    const canvas = page.locator('#progressChart');
    await expect(canvas).toBeVisible();

    // Wait for Chart.js to render
    await page.waitForTimeout(500);

    const boundingBox = await canvas.boundingBox();
    expect(boundingBox).not.toBeNull();
    expect(boundingBox!.width).toBeGreaterThan(0);
  });
});
