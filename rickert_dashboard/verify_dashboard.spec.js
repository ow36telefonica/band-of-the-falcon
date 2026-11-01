// verify_dashboard.spec.js
const { test, expect } = require('@playwright/test');
const path = require('path');

test.describe('Rickert Dashboard Verification', () => {
  const htmlPath = 'file://' + path.resolve(__dirname, 'dashboard.html');

  test('1. Initial UI Elements and Grid Structure', async ({ page }) => {
    await page.goto(htmlPath);
    
    // タイトルの確認
    await expect(page).toHaveTitle(/RICKERT/);
    
    // 主要パネルの存在確認
    await expect(page.locator('.logistics-col')).toBeVisible();
    await expect(page.locator('.comm-col')).toBeVisible();
    await expect(page.locator('.forge-col')).toBeVisible();
    
    // ヘッダーのロゴ確認
    await expect(page.locator('header h1')).toHaveText('Rickert');
  });

  test('2. Responsive Design Vulnerability Check', async ({ page }) => {
    await page.goto(htmlPath);
    
    // 画面サイズをスマホサイズ（縦長）にする
    await page.setViewportSize({ width: 375, height: 812 });
    
    // grid-template-columns が固定ピクセル (320px 1fr 360px) になっているため、
    // 横幅が375pxのときに横スクロールが発生しているか、要素がはみ出しているかを確認
    const mainWidth = await page.evaluate(() => {
      const main = document.querySelector('main');
      return main.scrollWidth > window.innerWidth;
    });
    
    console.log(`[Recon Check] Horizontal Scroll on Mobile: ${mainWidth ? 'YES (Vulnerable)' : 'NO'}`);
  });

  test('3. Easter Egg (Sacrifice Ceremony) Interaction and Conflict Check', async ({ page }) => {
    await page.goto(htmlPath);
    
    // チャット入力欄に「ガッツを捧げる」と入力
    const input = page.locator('#comm-input');
    await input.fill('ガッツを捧げる');
    
    // 送信
    await page.click('#comm-send-btn');
    
    // 蝕の儀式メッセージが表示されたか確認
    const eclipseMsg = page.locator('.sender-eclipse');
    await expect(eclipseMsg).toBeVisible();
    
    // ガッツが烙印状態になったか確認
    const gutsRoster = page.locator('.roster-item.branded');
    await expect(gutsRoster).toBeVisible();
    
    // トークンメーターが跳ね上がったか確認
    const tokenVal = await page.locator('#token-val').innerText();
    expect(tokenVal).toContain('113,230');
    
    // 3.5秒待つ (Fetchの周期3秒をまたぐ)
    await page.waitForTimeout(3500);
    
    // 【競合バグの検証】
    // バックグラウンドFetchにより、リソースメーターがサーバーデータ（68,230）に上書きされて戻ってしまっていないか確認
    const tokenValAfterFetch = await page.locator('#token-val').innerText();
    console.log(`[Recon Check] Token Value after 3s Fetch: ${tokenValAfterFetch}`);
  });
});
