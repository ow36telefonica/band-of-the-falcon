// 24:00:30 JST まで待機して Google Sheets を自動更新するスクリプト
const { execSync } = require('child_process');

const targetJST = new Date();
// 翌日 00:00:30 JST (2026-09-30 00:00:30)
targetJST.setDate(targetJST.getDate() + 1);
targetJST.setHours(0, 0, 30, 0);

const waitMs = targetJST.getTime() - Date.now();

console.log(`[Auto Sheet Updater] Target time: ${targetJST.toLocaleString('ja-JP')}`);
console.log(`[Auto Sheet Updater] Waiting ${Math.round(waitMs / 1000)} seconds (${(waitMs / 60000).toFixed(1)} minutes)...`);

setTimeout(async () => {
  console.log('[Auto Sheet Updater] 24:00 reached! Updating Google Sheets...');
  try {
    // 35行目: 壮年ダブルス大会要項掲載
    console.log('Updating Row 35...');
    const out35 = execSync('node manage-sheet.js update 2026年度 35 2 "schedule/2026.php, index.php, pdf/20261211_entry.pdf"', { cwd: __dirname });
    console.log(out35.toString());

    // 36行目: 男子シードチャレンジ大会 抽選結果
    console.log('Updating Row 36...');
    const out36 = execSync('node manage-sheet.js update 2026年度 36 1 "index.php"', { cwd: __dirname });
    console.log(out36.toString());

    console.log('[Auto Sheet Updater] All rows successfully updated to 完了!');
  } catch (err) {
    console.error('[Auto Sheet Updater] Error updating sheet:', err);
  }
}, Math.max(waitMs, 1000));
