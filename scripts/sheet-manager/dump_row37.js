const { GoogleSpreadsheet } = require('google-spreadsheet');
const { JWT } = require('google-auth-library');

const SPREADSHEET_ID = '1uR33VUcSIVwLNz5eKbgo5K6bTc8Tty_Lhq5KVCUkx4o';
const KEY_FILE = 'C:\\Users\\xanth\\.gemini\\keys\\project-17a1beab-7091-49c2-abf-194f51168a14.json';
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
  await sheet.loadHeaderRow();
  const rows = await sheet.getRows();
  // 37行目 = row index 35 (2行目がindex 0なので)
  const row = rows[35];
  console.log('--- Row 37 Details ---');
  sheet.headerValues.forEach((header, idx) => {
    const val = row.get(header) || row._rawData[idx] || '';
    if (val) {
      console.log(`[${header}] : ${val}`);
    }
  });
}

run().catch(console.error);
