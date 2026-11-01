# 鷹の団 統合リポジトリ (Band of the Falcon)

本リポジトリは、Google Antigravity / Gemini CLI 環境において最高の戦闘力を発揮する自律型AIチーム「鷹の団」の全頭脳・兵站・自動化ツール群を統合管理し、いかなるPC環境へもワンコマンドで神速移植できるように設計されたマスターリポジトリです。

---

## 1. 鷹の団 編制一覧 (Roster)

* **最高責任者**: グリフィス団長（修さん）
* **千人長 (司令塔)**: キャスカ（Gemini / 一人称: 私）
* **団員 (サブエージェント)**:
  * **ガストン (`@gaston-strategist`)**: 依頼解析・作戦計画立案。
  * **ガッツ (`@guts-modernizer`)**: ソース改修・切り込み実行。
  * **コルカス (`@corkus-validator`)**: 内部検証・軍規チェック。
  * **ジュドー (`@judeau-checker`)**: 外部検証・Playwright E2E偵察。
  * **ピピン (`@pippin-transporter`)**: Git管理・本番デプロイ。
  * **エリカ (`@erica-blacksmith`)**: 兵站ダッシュボード修理・UI鋳造。
  * **ファルネーゼ (`@farnese-chronicler`)**: 戦記・デイリーログ執筆。

---

## 2. ディレクトリ構成

```text
band-of-the-falcon/
├── GEMINI.md                  # 全体軍規・ペルソナ定義（第1条〜第12条）
├── .gemini/
│   ├── agents/                # 全団員プロンプト (gaston, guts, corkus, judeau...)
│   └── config/skills/         # スキル群 (hawk-deployment, codex-debate...)
├── rickert_dashboard/         # 兵站司令室 (dashboard.html, update_logistics.py, assets)
├── antigravity_indicator/     # モニターインジケーター (start_all.py 等)
├── scripts/
│   └── sheet-manager/         # Google Sheets 依頼管理表連携スクリプト
├── install.py                 # 【神速移植】新PC用自動展開スクリプト
├── sync_from_local.py         # メインPC上の最新変更を本リポジトリへ吸い上げる同期スクリプト
├── .gitignore                 # 認証鍵 (keys/*.json) や機密ファイルの物理遮断
└── README.md                  # 本マニュアル
```

---

## 3. 新PCへの移植手順（3ステップ）

### Step 1: リポジトリのクローン
新PCのターミナルで本リポジトリをクローンします。
```bash
git clone git@github.com:ow36telefonica/band-of-the-falcon.git C:\Users\<ユーザー名>\band-of-the-falcon
cd C:\Users\<ユーザー名>\band-of-the-falcon
```

### Step 2: 自動インストーラーの実行
```bash
python install.py
```
* ホームディレクトリ（`~`）直下への `GEMINI.md` 配置
* `~/.gemini/agents` への全団員配備
* `~/.gemini/config/skills` へのスキル配備
* `~/antigravity_indicator` および `~/scripts/sheet-manager` の配備＆依存パッケージのインストールが全自動で完了します。

### Step 3: サービスアカウント認証鍵の配備
Google Sheets 連携に必要な認証鍵 JSON を以下のフォルダに配置します：
* `C:\Users\<ユーザー名>\.gemini\keys\project-17a1beab-7091-49c2-abf-194f51168a14.json`

以上で、新PC上でもメインPCとまったく同一の「鷹の団」が即座に活性化します。

---

## 4. 日常の運用・同期フロー

メインPCで軍規（`GEMINI.md`）や団員プロンプト、スクリプトを進化させた際は、以下の手順でリポジトリを最新化します：

```bash
# 1. ローカルの最新リソースを本リポジトリへ吸い上げ
python C:\Users\xanth\band-of-the-falcon\sync_from_local.py

# 2. Git コミット & プッシュ
cd C:\Users\xanth\band-of-the-falcon
git add .
git commit -m "feat: 軍規およびエージェントの最新化"
git push origin main
```

他PCでは `git pull` して `python install.py` を実行するだけで、最新の軍規・能力が即時同期されます。
