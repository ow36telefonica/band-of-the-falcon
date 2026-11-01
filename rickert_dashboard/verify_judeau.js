const { chromium } = require('playwright');
const fs = require('fs');
async function run() {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  const client = await page.context().newCDPSession(page);
  await client.send('Network.setCacheDisabled', { cacheDisabled: true });
  const url = 'file:///C:/Users/xanth/Dropbox/個人請負/品川区テニス連盟/hp/docs/rickert_dashboard/dashboard.html';
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.screenshot({ path: 'C:/Users/xanth/dashboard_judeau_verify.png', fullPage: true });
  console.log('Dashboard verified with no-cache');
  await browser.close();
}
run();
