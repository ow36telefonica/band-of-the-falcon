# 【鷹の団】別PC展開・環境移行完全マニュアル (Band of the Falcon Migration Guide)

本ドキュメントは、別のPC（サブPC・新設マシン）において「鷹の団」の全戦力・軍規・ツール群を寸分違わず一発でセットアップし、完全活性化させるための標準運用手順書です。

---

## 1. 前提条件 (事前準備)

新PC側で以下の基本ツールがインストールされていることを確認してください：
* **Git**: `git --version`
* **Python (3.10以上推奨)**: `python --version`
* **Node.js**: `node --version`（依頼管理表連携スクリプトの実行に必要）

---

## 2. 初回セットアップ手順 (完全3ステップ)

### Step 1: リポジトリのクローン (Git Clone)
PowerShell または ターミナルを開き、GitHub プライベートリポジトリを取得します：

```powershell
# ユーザーホーム直下へクローン
cd $HOME
git clone https://github.com/ow36telefonica/band-of-the-falcon.git
cd band-of-the-falcon
```

---

### Step 2: 自動インストーラーの実行 (Install)
同梱の神速展開スクリプトを実行します：

```powershell
python install.py
```

> [!NOTE]
> **このコマンド一発で以下の全環境が自動配備されます：**
> 1. **全体軍規の配備**: `$HOME\GEMINI.md`（第1条〜第13条）
> 2. **全団員プロンプトの配備**: `$HOME\.gemini\agents\`（ガストン、ガッツ、コルカス、ジュドー、ピピン、エリカ、ファルネーゼ）
> 3. **スキル群の配備**: `$HOME\.gemini\config\skills\`（リッケルト起動、codex-debate等）
> 4. **司令室モニターの配備**: `$HOME\antigravity_indicator\`
> 5. **業務スクリプトの配備**: `$HOME\scripts\sheet-manager\`（`npm install` も自動実行）

---

### Step 3: サービスアカウント認証鍵の配備 (Credential)
セキュリティ上、GitHub には含めていない Google サービスアカウント秘密鍵（JSON）を、メインPCから安全な手段（USBメモリ、1Password、Bitwarden等）でコピーし、新PCの以下の定位置へ配置してください：

* **配置先フォルダ**: `C:\Users\<ユーザー名>\.gemini\keys\`
* **ファイル名**: `project-17a1beab-7091-49c2-abf-194f51168a14.json`

---

## 3. 開戦・動作確認チェックリスト

配備完了後、正常に活性化されているかを以下の順で点検します：

- [ ] **軍規の存在確認**: ホーム直下に `GEMINI.md` が存在するか
- [ ] **エージェント認識確認**: Antigravity または Gemini CLI を起動した際、ペルソナ（キャスカ・各団員）が認識されているか
- [ ] **リッケルト起動確認**: 「鷹の団、出陣！」の合図で兵站ダッシュボードおよびインジケーターが起動するか
- [ ] **台帳連携確認**: `node $HOME\scripts\sheet-manager\manage-sheet.js list` を実行し、依頼管理表の未対応タスクが取得できるか

---

## 4. 日常の同期フロー (2回目以降の運用)

### メインPC側
* **操作不要（完全自動）**:
  常駐監視プロセス（`update_logistics.py`）により、軍規やエージェントを変更すると自動的に GitHub へ差分プッシュされます。

### 別PC（サブPC）側
メインPC側で進化させた最新の軍規や能力を取り込む際は、以下の **2コマンドを実行するだけ** で最新化されます：

```powershell
cd $HOME\band-of-the-falcon
git pull
python install.py
```

---

## 5. トラブルシューティング

### Q1. `python install.py` で権限エラー（PermissionError）が出る
* **対処**: PowerShell を「管理者として実行」するか、開いているエディタ（VSCode等）がファイルをロックしていないか確認してください。

### Q2. `manage-sheet.js` で認証エラーになる
* **対処**: `Step 3` の秘密鍵（JSON）が `C:\Users\<ユーザー名>\.gemini\keys\project-17a1beab-7091-49c2-abf-194f51168a14.json` に正しく置かれているか、ファイル名に過不足がないかを確認してください。

### Q3. Git クローン時にアクセス拒否（Permission denied）される
* **対処**: `band-of-the-falcon` は Private リポジトリのため、新PCの GitHub アカウント（または Personal Access Token / SSHキー）が認証されていることを確認してください。
