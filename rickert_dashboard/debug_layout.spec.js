const { test, expect } = require('@playwright/test');
const path = require('path');

test('Check console and layout', async ({ page }) => {
  const htmlPath = 'file://' + path.resolve(__dirname, 'dashboard.html');
  const logs = [];
  page.on('console', msg => logs.push(`[${msg.type()}] ${msg.text()}`));
  page.on('pageerror', err => logs.push(`[ERROR] ${err.message}`));
  
  await page.setViewportSize({ width: 1200, height: 800 });
  await page.goto(htmlPath, { waitUntil: 'networkidle' });
  
  // Wait a bit for JS to execute
  await page.waitForTimeout(2000);
  
  console.log("--- BROWSER LOGS ---");
  logs.forEach(l => console.log(l));
  console.log("--------------------");

  // Check positions of elements
  const mainRect = await page.locator('main').boundingBox();
  const logisticsRect = await page.locator('.logistics-col').boundingBox();
  const commRect = await page.locator('.comm-col').boundingBox();
  const forgeRect = await page.locator('.forge-col').boundingBox();
  
  console.log('mainRect:', mainRect);
  console.log('logisticsRect:', logisticsRect);
  console.log('commRect:', commRect);
  console.log('forgeRect:', forgeRect);
});