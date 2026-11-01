import { test, expect } from '@playwright/test';

const BASE_URL = 'https://shinagawa-tennis-a.com/';

test.describe('全更新対象URL 最終一括検証', () => {

  const TARGETS = [
    { name: 'トップページ', url: '' },
    { name: 'スケジュール(2026)', url: 'schedule/2026.php' },
    { name: '大会結果(2026)', url: 'result/2026.php' },
    { name: 'レポート一覧', url: 'report/index.php' },
    { name: '女子シードチャレンジ結果', url: 'report/20260510.php' },
    { name: '平日女子選手権レポート', url: 'report/20260403.php' },
    { name: 'スケジュールPDF', url: 'pdf/2026_schedule.pdf', type: 'download' }
  ];

  for (const target of TARGETS) {
    test(`検証: ${target.name}`, async ({ page }) => {
      const fullUrl = `${BASE_URL}${target.url}`;
      console.log(`検証中: ${fullUrl}`);

      if (target.type === 'download') {
        const response = await page.request.get(fullUrl);
        expect(response.status()).toBe(200);
        console.log(`✅ OK: ${target.name} (Downloadable)`);
      } else {
        const response = await page.goto(fullUrl);
        expect(response?.status()).toBe(200);
        console.log(`✅ OK: ${target.name} (Status 200)`);
        
        if (target.url === 'report/20260403.php') {
            await expect(page.locator('body')).toContainText('渡邉・大野');
            console.log('✅ OK: キャプション修正を確認');
        }
      }
    });
  }
});
