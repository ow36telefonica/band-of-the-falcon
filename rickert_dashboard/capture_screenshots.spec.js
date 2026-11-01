const { test } = require('@playwright/test');
test('Capture Screenshots with No-Cache', async ({ page }) => {
  const client = await page.context().newCDPSession(page);
  await client.send('Network.setCacheDisabled', { cacheDisabled: true });
  const url = 'file://' + require('path').resolve(__dirname, 'dashboard.html');
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.screenshot({ path: 'desktop_initial.png' });
});
