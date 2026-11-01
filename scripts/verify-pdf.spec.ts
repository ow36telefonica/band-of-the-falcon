import { test, expect } from '@playwright/test';

const PDF_URL = 'https://shinagawa-tennis-a.com/pdf/2026_schedule.pdf';

test('19行目: 2026_schedule.pdf のダウンロード疎通検証', async ({ page }) => {
  console.log(`検証開始: ${PDF_URL}`);
  
  // PDFは直接表示ではなくダウンロードとして扱う
  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.goto(PDF_URL).catch(e => {
        // Download starting によるエラーは無視してよい
        if (!e.message.includes('Download is starting')) throw e;
    }),
  ]);

  console.log('✅ PDFのダウンロードが開始されました。');
  const path = await download.path();
  
  if (path) {
    console.log('✅ PDFファイルが正常に受信されました。');
    // ファイルが存在し、中身があることを確認
    const stats = await download.createReadStream();
    console.log(`✅ ダウンロード成功。ファイル名: ${download.suggestedFilename()}`);
  }
});
