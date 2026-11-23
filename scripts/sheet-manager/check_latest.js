const { GoogleSpreadsheet } = require('google-spreadsheet');
const { JWT } = require('google-auth-library');
const path = require('path');
const os = require('os');
const fs = require('fs');

const SPREADSHEET_ID = '1uR33VUcSIVwLNz5eKbgo5K6bTc8Tty_Lhq5KVCUkx4o';

function findLatestKeyFile() {
  if (process.env.GOOGLE_SHEETS_KEY_FILE && fs.existsSync(process.env.GOOGLE_SHEETS_KEY_FILE)) {
    return process.env.GOOGLE_SHEETS_KEY_FILE;
  }
  const keysDir = path.join(os.homedir(), '.gemini', 'keys');
  const files = fs.readdirSync(keysDir)
    .filter(f => f.endsWith('.json') && !f.endsWith('.bak'))
    .map(f => ({
      name: f,
      path: path.join(keysDir, f),
      mtime: fs.statSync(path.join(keysDir, f)).mtimeMs
    }))
    .sort((a, b) => b.mtime - a.mtime);
  return files[0].path;
}

const KEY_FILE = findLatestKeyFile();
const creds = require(KEY_FILE);

const serviceAccountAuth = new JWT({
  email: creds.client_email,
  key: creds.private_key,
  scopes: ['https://www.googleapis.com/auth/spreadsheets'],
});

const doc = new GoogleSpreadsheet(SPREADSHEET_ID, serviceAccountAuth);

async function run() {
  await doc.loadInfo();
  const sheet = doc.sheetsByTitle['2026年度'];
  if (!sheet) {
    console.error('2026年度シートが見つかりません');
    return;
  }
  await sheet.loadHeaderRow();
  const rows = await sheet.getRows();
  console.log(`=== 2026年度 全${rows.length}行 ===`);
  
  // 40行目以降を表示
  for (let i = Math.max(0, rows.length - 15); i < rows.length; i++) {
    const row = rows[i];
    const rowNum = i + 2;
    const content = row.get('依頼内容（対象の試合・及びその開催日も併記ください）') || '';
    const status = row.get('ステータス') || '未';
    const detail = row._rawData[13] || '';
    const date = row.get('受付日') || row.get('タイムスタンプ') || '';
    console.log(`行${rowNum}: [${status}] 受付:${date}`);
    console.log(`  内容: ${content}`);
    if (detail) console.log(`  詳細: ${detail}`);
  }
}

run().catch(console.error);
