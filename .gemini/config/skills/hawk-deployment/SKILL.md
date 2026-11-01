---
name: hawk-deployment
description: 新生「鷹の団」の出撃（兵站ダッシュボード「リッケルト」の起動・連動）を自動化する。ユーザーが「鷹の団、出陣！」や「リッケルトを起動して」と言った際にトリガーする。
---

# 🦅 鷹の団、出陣！ (Hawk's Unit, Deploy!)

このスキルは、品川区テニス連盟HP運用チーム「鷹の団」の兵站監視システム「リッケルト」を即座に起動し、現在の会話ログとの同期を開始するための手順を定めたものである。

## ⚔️ 出撃ワークフロー (Deployment Workflow)

ユーザーから「出陣」の号令がかかった場合、以下の手順を**一気呵成に**実行せよ。

1.  **兵站データの強制同期**:
    `update_logistics.py` を実行して、現在のセッションの最新ログを `logistics_data.js` に書き出す。
    ```powershell
    python C:\Users\xanth\Dropbox\個人請負\品川区テニス連盟\hp\docs\rickert_dashboard\update_logistics.py --once
    ```

2.  **監視プロセスの起動 (バックグラウンド)**:
    リアルタイム更新を維持するため、監視ループをバックグラウンドで起動する。
    ```powershell
    # run_shell_command の is_background: true を使用
    python C:\Users\xanth\Dropbox\個人請負\品川区テニス連盟\hp\docs\rickert_dashboard\update_logistics.py
    ```

3.  **団長（ユーザー）への報告**:
    出撃完了の報告と共に、ダッシュボードのローカルリンクを提示せよ。
    - **ダッシュボードURL**: `file:///C:/Users/xanth/Dropbox/%E5%80%8B%E4%BA%BA%E8%AB%8B%E8%B2%A0/%E5%93%81%E5%B7%9D%E5%8C%BA%E3%83%86%E3%83%8B%E3%82%B9%E9%80%A3%E7%9B%9F/hp/docs/rickert_dashboard/dashboard.html`

## 🛡️ 軍規 (Operational Rules)

- **自動スクロールの確認**: 最新の戦況（チャットログ）が常に一番下に表示されるよう、`dashboard.html` が修正済みであることを前提とする。
- **CORS回避**: `logistics_data.js` (JS注入方式) を使用しているため、特別なサーバーを立てる必要はなく、ブラウザで直接開くだけでよい。
- **兵站意識**: ダッシュボードの起動自体が兵站（リソース）を消費していることを自覚し、無駄なリクエストが発生しないよう監視ループの挙動に注意せよ。

## 🏹 出撃時の口上例

> 「はっ、グリフィス団長（修さん）！新生『鷹の団』、ただちに出撃いたします！」
> 「リッケルト起動……兵站同期完了。これより戦況のリアルタイム監視を開始します！」
