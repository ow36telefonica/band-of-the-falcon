const { chromium } = require('playwright');
async function run() {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  const client = await page.context().newCDPSession(page);
  await client.send('Network.setCacheDisabled', { cacheDisabled: true });
  console.log('--- No-Cache Recon ---');
  await page.goto('http://shinagawa-tennis.main.jp/index.php', { waitUntil: 'networkidle' });
  await page.screenshot({ path: 'C:/Users/xanth/recon_site_nocache.png' });
  console.log('Done');
  await browser.close();
}
run();
