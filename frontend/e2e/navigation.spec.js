// navigation.spec.js
const { test, expect } = require('@playwright/test');

test.describe('Navigation Tests', () => {
  test('should navigate to the dashboard page', async ({ page }) => {
    // Start from the home page
    await page.goto('/');
    
    // Find and click the dashboard link
    await page.getByRole('link', { name: /dashboard/i }).click();
    
    // The URL should now include "/dashboard"
    await expect(page).toHaveURL(/.*dashboard/);
    
    // The page should contain the dashboard title
    await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
  });

  test('should navigate to the projections page', async ({ page }) => {
    // Start from the home page
    await page.goto('/');
    
    // Find and click the projections link
    await page.getByRole('link', { name: /projections/i }).click();
    
    // The URL should now include "/projections"
    await expect(page).toHaveURL(/.*projections/);
    
    // The page should contain the projections title
    await expect(page.getByRole('heading', { name: /projections/i })).toBeVisible();
  });

  test('should navigate to the historical page', async ({ page }) => {
    // Start from the home page
    await page.goto('/');
    
    // Find and click the historical link
    await page.getByRole('link', { name: /historical/i }).click();
    
    // The URL should now include "/historical"
    await expect(page).toHaveURL(/.*historical/);
    
    // The page should contain the historical title
    await expect(page.getByRole('heading', { name: /historical/i })).toBeVisible();
  });

  test('should navigate to the upload page', async ({ page }) => {
    // Start from the home page
    await page.goto('/');
    
    // Find and click the upload link
    await page.getByRole('link', { name: /upload/i }).click();
    
    // The URL should now include "/upload"
    await expect(page).toHaveURL(/.*upload/);
    
    // The page should contain the upload title
    await expect(page.getByRole('heading', { name: /upload/i })).toBeVisible();
  });
});
