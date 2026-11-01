const { GoogleSpreadsheet } = require('google-spreadsheet');
const { JWT } = require('google-auth-library');

const path = require('path');
const os = require('os');

const SPREADSHEET_ID = '1uR33VUcSIVwLNz5eKbgo5K6bTc8Tty_Lhq5KVCUkx4o';
const KEY_FILE = process.env.GOOGLE_SHEETS_KEY_FILE || path.join(os.homedir(), '.gemini', 'keys', 'project-17a1beab-7091-49c2-abf-194f51168a14.json');
const creds = require(KEY_FILE);

const serviceAccountAuth = new JWT({
  email: creds.client_email,
  key: creds.private_key,
  scopes: ['https://www.googleapis.com/auth/spreadsheets'],
});

const doc = new GoogleSpreadsheet(SPREADSHEET_ID, serviceAccountAuth);

const COL_CONTENT = '依頼内容（対象の試合・及びその開催日も併記ください）';
const COL_STATUS = 'ステータス';
const COL_PUBLISH_DATE = '公開日';
const COL_FILE_COUNT = '更新対象ファイル数';
const COL_INDEX_DETAIL = 13; // N列
const COL_INDEX_FILES = 14;  // O列

// 特殊指示・重要変更キーワード群
const SPECIAL_KEYWORDS = [
  '削除', '消去', '消して', '非表示', '消す',
  'お詫び', '訂正', '修正', '差替', '差し替え',
  '至急', '緊急', '注意', '戻す', '取り下げ', '非公開'
];

/**
 * テキストから特殊指示（削除・訂正等）を検知・抽出する
 */
function extractSpecialInstructions(text) {
  if (!text) return null;
  const matchedKeywords = [];
  const matchedSentences = [];

  for (const kw of SPECIAL_KEYWORDS) {
    if (text.includes(kw)) {
      matchedKeywords.push(kw);
    }
  }

  if (matchedKeywords.length === 0) return null;

  // 句点や改行で文章を分割し、該当文を特定
  const lines = text.split(/[\r\n。]+/).map(s => s.trim()).filter(Boolean);
  for (const line of lines) {
    if (matchedKeywords.some(kw => line.includes(kw))) {
      matchedSentences.push(line);
    }
  }

  return {
    keywords: Array.from(new Set(matchedKeywords)),
    sentences: Array.from(new Set(matchedSentences))
  };
}

// 現在の年度を取得 (4月始まり)
function getFiscalYear(date = new Date()) {
  const month = date.getMonth() + 1;
  const year = date.getFullYear();
  return month >= 4 ? year : year - 1;
}

async function run() {
  await doc.loadInfo();
  const command = process.argv[2];

  if (command === 'list') {
    console.log(`--- 全シート 未対応タスク一覧 ---`);
    for (const sheet of doc.sheetsByIndex) {
      const title = sheet.title;
      try {
        await sheet.loadHeaderRow();
      } catch (err) {
        // ヘッダー行が存在しないシート（空シート等）は安全にスキップ
        continue;
      }
      const rows = await sheet.getRows();
      rows.forEach((row, index) => {
        const status = row.get(COL_STATUS);
        if (!['処理済み', '公開済み', '完了', '済'].includes(status) && row.get(COL_CONTENT)) {
          const content = row.get(COL_CONTENT) || '';
          const detailRaw = row._rawData[COL_INDEX_DETAIL] || '';
          const fullText = `${content} ${detailRaw}`;
          
          const alert = extractSpecialInstructions(fullText);
          const alertTag = alert ? `\x1b[31m【特殊指示あり: ${alert.keywords.join(', ')}】\x1b[0m` : '';
          const detailTag = detailRaw ? '【詳細あり】' : '';
          
          console.log(`[${title}] ${index + 2}行目: ${content.substring(0, 35)} ${detailTag} ${alertTag} [${status || '未'}]`);
        }
      });
    }
  }
  else if (command === 'get' || command === 'update') {
    const sheetName = process.argv[3];
    const rowIndex = parseInt(process.argv[4]) - 2;
    const fileCount = process.argv[5] || '1';
    const fileList = process.argv[6] || '';

    const sheet = doc.sheetsByTitle[sheetName];
    if (!sheet) {
      console.error(`エラー: シート「${sheetName}」が見つかりません。`);
      return;
    }

    try {
      await sheet.loadHeaderRow();
    } catch (err) {
      console.error(`エラー: シート「${sheetName}」のヘッダーを読み込めません。`);
      return;
    }

    const rows = await sheet.getRows();
    const row = rows[rowIndex];

    if (!row) {
      console.error('エラー: 指定された行が見つかりません。');
      return;
    }

    if (command === 'get') {
      console.log(`--- [${sheetName}] ${rowIndex + 2}行目の詳細 ---`);
      let accumulatedText = '';
      sheet.headerValues.forEach((header, idx) => {
        const val = row.get(header) || row._rawData[idx] || '';
        if (val) {
          console.log(`[${header}]: ${val}`);
          accumulatedText += ' ' + val;
        }
      });

      // 【ガストン特殊指示アラート判定】
      const alert = extractSpecialInstructions(accumulatedText);
      if (alert) {
        console.log('\n\x1b[41m\x1b[37m================================================================================\x1b[0m');
        console.log(`\x1b[33m⚠️  【ガストン特殊指示アラート】本文中に重要変更・特殊指示が検出されました！\x1b[0m`);
        console.log(`    検知キーワード: [ \x1b[31m${alert.keywords.join(', ')}\x1b[0m ]`);
        console.log('    要注意文章:');
        alert.sentences.forEach(s => {
          console.log(`      \x1b[36m> "${s}"\x1b[0m`);
        });
        console.log('\x1b[41m\x1b[37m================================================================================\x1b[0m\n');
      }
    } else {
      row.set(COL_STATUS, '完了');
      row.set(COL_PUBLISH_DATE, new Date().toLocaleDateString('ja-JP'));
      row.set(COL_FILE_COUNT, fileCount);
      if (row._rawData.length > COL_INDEX_FILES) {
        row._rawData[COL_INDEX_FILES] = fileList; 
      }
      await row.save();
      console.log(`成功: ${sheetName} の ${rowIndex + 2}行目を「処理済み」に更新しました。`);
      if (fileList) console.log(`対象ファイル: ${fileList}`);
    }
  }
}

run().catch(err => console.error(err));
