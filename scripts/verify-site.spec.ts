import { test, expect } from '@playwright/test';

// 検証対象のベースURL
const BASE_URL = 'https://shinagawa-tennis-a.com/';

// 今回修正した可能性のある特定のパス
const MODIFIED_PATHS = [
  'index.php',
];

test.describe('品川区テニス連盟HP 公開後検証', () => {

  test('トップページと主要リンクの検証', async ({ page }) => {
    console.log(`検証開始: ${BASE_URL}`);
    
    // 1. サイトにアクセス
    await page.goto(BASE_URL);
    await expect(page).toHaveTitle(/品川区テニス連盟/);
    console.log('✅ トップページの表示とタイトルを確認しました。');

    // 2. What's New セクションのPDFリンクをチェック
    console.log('--- PDFリンクの疎通確認 ---');
    const pdfLinks = page.locator('a[href$=".pdf"]');
    const count = await pdfLinks.count();
    
    for (let i = 0; i < Math.min(count, 5); i++) {
      const link = pdfLinks.nth(i);
      const href = await link.getAttribute('href');
      const text = (await link.innerText()).trim();
      
      if (href) {
        const fullUrl = new URL(href, BASE_URL).href;
        try {
          const response = await page.request.get(fullUrl);
          if (response.status() === 200) {
            console.log(`✅ OK: [${text}] -> ${href}`);
          } else {
            console.error(`❌ NG: [${text}] -> ${href} (Status: ${response.status()})`);
          }
        } catch (e) {
          console.error(`❌ エラー: ${href} へのアクセスに失敗しました。`);
        }
      }
    }
  });

  // 修正した特定のページがあれば、個別にチェック
  for (const path of MODIFIED_PATHS) {
    if (path === 'index.php') continue;
    
    test(`個別ページ検証: ${path}`, async ({ page }) => {
      const targetUrl = new URL(path, BASE_URL).href;
      console.log(`検証中: ${targetUrl}`);
      
      const response = await page.goto(targetUrl);
      expect(response?.status()).toBe(200);
      console.log(`✅ ${path} の表示を確認しました。`);
    });
  }
});
