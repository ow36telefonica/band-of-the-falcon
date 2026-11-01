# -*- coding: utf-8 -*-
"""
auto_sync_push.py
【ピピン自動輸送】鷹の団 変更検知＆自動GitHub同期スクリプト

ローカルの鷹の団リソース（軍規、団員、スキル、司令室、スクリプト）を吸い上げ、
差分が存在する場合のみ自動でコミット＆GitHub（origin/main）へプッシュする。
"""

import os
import sys
import shutil
import glob
import subprocess
import datetime

def sync_resources(falcon_root):
    """ローカルの最新リソースをリポジトリへコピー"""
    # 1. GEMINI.md
    src_gemini = r"C:\Users\xanth\GEMINI.md"
    if os.path.exists(src_gemini):
        shutil.copy2(src_gemini, os.path.join(falcon_root, "GEMINI.md"))

    # 2. 団員プロンプト (.gemini/agents)
    agents_dest = os.path.join(falcon_root, ".gemini", "agents")
    os.makedirs(agents_dest, exist_ok=True)
    agents_src = r"C:\Users\xanth\Dropbox\個人請負\品川区テニス連盟\hp\.gemini\agents"
    if os.path.exists(agents_src):
        for f in os.listdir(agents_src):
            src_file = os.path.join(agents_src, f)
            if os.path.isfile(src_file):
                shutil.copy2(src_file, agents_dest)

    # 3. スキル群 (.gemini/config/skills)
    skills_dest = os.path.join(falcon_root, ".gemini", "config", "skills")
    skills_src = r"C:\Users\xanth\.gemini\config\skills"
    if os.path.exists(skills_src):
        if os.path.exists(skills_dest):
            shutil.rmtree(skills_dest)
        shutil.copytree(skills_src, skills_dest)

    # 4. 兵站司令室 (rickert_dashboard)
    rickert_dest = os.path.join(falcon_root, "rickert_dashboard")
    os.makedirs(rickert_dest, exist_ok=True)
    rickert_src = r"C:\Users\xanth\Dropbox\個人請負\品川区テニス連盟\hp\docs\rickert_dashboard"
    if os.path.exists(rickert_src):
        for item in os.listdir(rickert_src):
            if "競合" in item or item.endswith(".log") or item in ("__pycache__", "log"):
                continue
            s = os.path.join(rickert_src, item)
            d = os.path.join(rickert_dest, item)
            if os.path.isdir(s):
                if os.path.exists(d):
                    shutil.rmtree(d)
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)

    # 5. モニターインジケーター (antigravity_indicator)
    indicator_dest = os.path.join(falcon_root, "antigravity_indicator")
    indicator_src = r"C:\Users\xanth\antigravity_indicator"
    if os.path.exists(indicator_src):
        if os.path.exists(indicator_dest):
            shutil.rmtree(indicator_dest)
        shutil.copytree(indicator_src, indicator_dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    # 6. 業務スクリプト (scripts)
    scripts_dest = os.path.join(falcon_root, "scripts")
    sheet_dest = os.path.join(scripts_dest, "sheet-manager")
    os.makedirs(sheet_dest, exist_ok=True)
    sheet_src = r"C:\Users\xanth\scripts\sheet-manager"
    if os.path.exists(sheet_src):
        for item in os.listdir(sheet_src):
            if item == "node_modules":
                continue
            s = os.path.join(sheet_src, item)
            d = os.path.join(sheet_dest, item)
            if os.path.isfile(s):
                shutil.copy2(s, d)

    for spec_file in glob.glob(r"C:\Users\xanth\scripts\verify-*.spec.ts"):
        shutil.copy2(spec_file, scripts_dest)


def check_and_push(falcon_root, quiet=False):
    """差分を検知して自動プッシュ"""
    # まず同期コピー
    sync_resources(falcon_root)

    # git status で差分確認
    status_res = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=falcon_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    if status_res.returncode != 0:
        if not quiet:
            print("【エラー】git status の実行に失敗しました。")
        return False

    changes = status_res.stdout.strip().splitlines()
    if not changes:
        if not quiet:
            print("【同期確認】差分なし。最新状態が維持されています。")
        return False

    changed_summary = []
    for c in changes[:5]:
        changed_summary.append(c.strip())
    if len(changes) > 5:
        changed_summary.append(f"...他 {len(changes)-5} 件")

    summary_text = ", ".join(changed_summary)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"auto(sync): 鷹の団リソース自動同期 ({now_str})\n\n変更検出: {summary_text}"

    print(f"【変更検知】鷹の団リソースに {len(changes)} 件の差分を検出しました。")
    print(f"  差分概要: {summary_text}")
    print("  自動コミット＆プッシュを開始します...")

    # git add -A
    subprocess.run(["git", "add", "-A"], cwd=falcon_root, check=True)

    # git commit
    commit_res = subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=falcon_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    if commit_res.returncode != 0:
        print(f"【エラー】コミット失敗: {commit_res.stderr}")
        return False

    # git push origin main
    push_res = subprocess.run(
        ["git", "push", "origin", "main"],
        cwd=falcon_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    if push_res.returncode == 0:
        print(f"【自動プッシュ成功】GitHub (origin/main) への同期が完了しました！ ({now_str})")
        return True
    else:
        print(f"【エラー】プッシュ失敗: {push_res.stderr}")
        return False


if __name__ == "__main__":
    falcon_dir = os.path.dirname(os.path.abspath(__file__))
    is_quiet = "--quiet" in sys.argv
    check_and_push(falcon_dir, quiet=is_quiet)
