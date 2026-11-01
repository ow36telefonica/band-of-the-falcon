# -*- coding: utf-8 -*-
"""
install.py
【神速移植】鷹の団 統合展開スクリプト (Band of the Falcon Installer)

新PCで本スクリプトを実行するだけで、
1. 全体軍規 GEMINI.md のホーム配備
2. 団員プロンプト (~/.gemini/agents) の配備
3. スキル群 (~/.gemini/config/skills) の配備
4. 兵站司令室・インジケーターの配備
5. 業務スクリプト (~/scripts/sheet-manager) の配備 & 依存解決
を一発で自動完了します。
"""

import sys
import os
import shutil
import subprocess

def get_home_dir():
    return os.path.expanduser("~")

def main():
    repo_root = os.path.dirname(os.path.abspath(__file__))
    home_dir = get_home_dir()

    print("==========================================================")
    print(" 鷹の団 新環境展開スクリプト (Band of the Falcon Installer)")
    print(f" 展開先ユーザーホーム: {home_dir}")
    print("==========================================================")

    # 1. GEMINI.md の配備
    print("\n[1/5] 全体軍規 GEMINI.md を配備中...")
    target_gemini = os.path.join(home_dir, "GEMINI.md")
    src_gemini = os.path.join(repo_root, "GEMINI.md")
    if os.path.exists(target_gemini):
        backup_gemini = os.path.join(home_dir, "GEMINI.md.bak")
        shutil.copy2(target_gemini, backup_gemini)
        print(f"  既存の GEMINI.md をバックアップしました: {backup_gemini}")
    shutil.copy2(src_gemini, target_gemini)
    print("  -> GEMINI.md 配備完了")

    # 2. 団員プロンプト (~/.gemini/agents)
    print("\n[2/5] 団員プロンプト (~/.gemini/agents) を配備中...")
    agents_dir = os.path.join(home_dir, ".gemini", "agents")
    os.makedirs(agents_dir, exist_ok=True)
    src_agents = os.path.join(repo_root, ".gemini", "agents")
    if os.path.exists(src_agents):
        for f in os.listdir(src_agents):
            sf = os.path.join(src_agents, f)
            df = os.path.join(agents_dir, f)
            shutil.copy2(sf, df)
            print(f"  団員配備: {f}")

    # 3. スキル群 (~/.gemini/config/skills)
    print("\n[3/5] スキル群 (~/.gemini/config/skills) を配備中...")
    skills_dir = os.path.join(home_dir, ".gemini", "config", "skills")
    os.makedirs(skills_dir, exist_ok=True)
    src_skills = os.path.join(repo_root, ".gemini", "config", "skills")
    if os.path.exists(src_skills):
        for s in os.listdir(src_skills):
            s_src = os.path.join(src_skills, s)
            s_dst = os.path.join(skills_dir, s)
            if os.path.isdir(s_src):
                if os.path.exists(s_dst):
                    shutil.rmtree(s_dst)
                shutil.copytree(s_src, s_dst)
                print(f"  スキル配備: {s}")

    # 4. インジケーター & 兵站ダッシュボード
    print("\n[4/5] 司令室インジケーター & 兵站司令室を配備中...")
    target_indicator = os.path.join(home_dir, "antigravity_indicator")
    src_indicator = os.path.join(repo_root, "antigravity_indicator")
    if os.path.exists(src_indicator):
        if not os.path.exists(target_indicator):
            shutil.copytree(src_indicator, target_indicator)
            print("  -> antigravity_indicator を配備完了")
        else:
            print("  -> antigravity_indicator は既に存在します（スキップ）")

    # 5. 業務スクリプト (~/scripts/sheet-manager)
    print("\n[5/5] 業務自動化スクリプト (~/scripts) を配備中...")
    target_scripts = os.path.join(home_dir, "scripts")
    target_sheet = os.path.join(target_scripts, "sheet-manager")
    os.makedirs(target_sheet, exist_ok=True)
    src_sheet = os.path.join(repo_root, "scripts", "sheet-manager")
    for item in os.listdir(src_sheet):
        s = os.path.join(src_sheet, item)
        d = os.path.join(target_sheet, item)
        if os.path.isfile(s):
            shutil.copy2(s, d)

    for item in os.listdir(os.path.join(repo_root, "scripts")):
        s = os.path.join(repo_root, "scripts", item)
        if os.path.isfile(s) and item.endswith(".ts"):
            shutil.copy2(s, os.path.join(target_scripts, item))

    # npm install の実行
    print("  Node.js 依存関係をインストール中...")
    try:
        subprocess.run(["npm", "install"], cwd=target_sheet, check=True, shell=True)
        print("  -> sheet-manager の npm install 完了")
    except Exception as e:
        print(f"  [注意] npm install に失敗しました（Node.js が未導入の場合は手動で実行してください）: {e}")

    # 認証鍵の案内
    print("\n" + "="*60)
    print("【展開完了】鷹の団の全兵装が配備されました！")
    print("="*60)
    keys_dir = os.path.join(home_dir, ".gemini", "keys")
    os.makedirs(keys_dir, exist_ok=True)
    print("【最終ステップ: 認証鍵の配置】")
    print(f"Google サービスアカウントの認証鍵 (JSON) を以下のフォルダに配置してください:")
    print(f"  >> {keys_dir}")
    print("\n配置後、直ちに「鷹の団」の全機能が活性化します。")
    print("="*60)

if __name__ == "__main__":
    main()
