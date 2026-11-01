import { test, expect } from '@playwright/test';

const BASE_URL = 'https://shinagawa-tennis-a.com/';

test.describe('管理表 17-18行目 詳細検証', () => {

  test('17行目: 女子シードチャレンジ結果の検証', async ({ page }) => {
    const targetUrl = `${BASE_URL}report/20260510.php`;
    console.log(`検証中: ${targetUrl}`);
    await page.goto(targetUrl);

    // テキストが含まれているかチェック
    const content = await page.innerText('body');
    
    const checkList = [
      '山下・萩原',
      '浜崎・笠間',
      '赤塚・伊藤',
      '水島・田久保'
    ];

    for (const name of checkList) {
      if (content.includes(name)) {
        console.log(`✅ 確認OK: 入賞者名 [${name}] が見つかりました。`);
      } else {
        console.error(`❌ 確認NG: 入賞者名 [${name}] が見つかりません。`);
      }
    }
  });

  test('18行目: 平日女子選手権キャプション修正の検証', async ({ page }) => {
    const targetUrl = `${BASE_URL}report/20260403.php`;
    console.log(`検証中: ${targetUrl}`);
    await page.goto(targetUrl);

    const content = await page.innerText('body');
    
    if (content.includes('渡邉・大野')) {
      console.log(`✅ 確認OK: 準優勝キャプションが [渡邉・大野] に修正されています。`);
    } else {
      console.error(`❌ 確認NG: 準優勝キャプション [渡邉・大野] が見つかりません。`);
    }
  });
});
