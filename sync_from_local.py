# -*- coding: utf-8 -*-
"""
sync_from_local.py
ローカルの鷹の団リソースを band-of-the-falcon へ安全に吸い上げて集約する
"""

import os
import shutil
import glob

falcon_root = os.path.dirname(os.path.abspath(__file__))

print("==========================================================")
print(" 鷹の団 リソース同期 (Local -> band-of-the-falcon)")
print("==========================================================")

# 1. GEMINI.md
print("[1/6] 全体軍規 GEMINI.md を同期中...")
shutil.copy2(r"C:\Users\xanth\GEMINI.md", os.path.join(falcon_root, "GEMINI.md"))

# 2. 団員プロンプト (.gemini/agents)
print("[2/6] 団員プロンプト (.gemini/agents) を同期中...")
agents_dest = os.path.join(falcon_root, ".gemini", "agents")
os.makedirs(agents_dest, exist_ok=True)
agents_src = r"C:\Users\xanth\Dropbox\個人請負\品川区テニス連盟\hp\.gemini\agents"
for f in os.listdir(agents_src):
    src_file = os.path.join(agents_src, f)
    if os.path.isfile(src_file):
        shutil.copy2(src_file, agents_dest)

# 3. スキル群 (.gemini/config/skills)
print("[3/6] スキル群 (.gemini/config/skills) を同期中...")
skills_dest = os.path.join(falcon_root, ".gemini", "config", "skills")
skills_src = r"C:\Users\xanth\.gemini\config\skills"
if os.path.exists(skills_dest):
    shutil.rmtree(skills_dest)
shutil.copytree(skills_src, skills_dest)

# 4. 兵站司令室 (rickert_dashboard)
print("[4/6] 兵站司令室 (rickert_dashboard) を同期中...")
rickert_dest = os.path.join(falcon_root, "rickert_dashboard")
os.makedirs(rickert_dest, exist_ok=True)
rickert_src = r"C:\Users\xanth\Dropbox\個人請負\品川区テニス連盟\hp\docs\rickert_dashboard"
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
print("[5/6] モニターインジケーター (antigravity_indicator) を同期中...")
indicator_dest = os.path.join(falcon_root, "antigravity_indicator")
indicator_src = r"C:\Users\xanth\antigravity_indicator"
if os.path.exists(indicator_dest):
    shutil.rmtree(indicator_dest)
shutil.copytree(indicator_src, indicator_dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

# 6. 業務スクリプト (scripts)
print("[6/6] 業務スクリプト (scripts) を同期中...")
scripts_dest = os.path.join(falcon_root, "scripts")
sheet_dest = os.path.join(scripts_dest, "sheet-manager")
os.makedirs(sheet_dest, exist_ok=True)
sheet_src = r"C:\Users\xanth\scripts\sheet-manager"
for item in os.listdir(sheet_src):
    if item == "node_modules":
        continue
    s = os.path.join(sheet_src, item)
    d = os.path.join(sheet_dest, item)
    if os.path.isfile(s):
        shutil.copy2(s, d)

for spec_file in glob.glob(r"C:\Users\xanth\scripts\verify-*.spec.ts"):
    shutil.copy2(spec_file, scripts_dest)

print("==========================================================")
print(" 同期完了！全リソースが band-of-the-falcon に集約されました。")
print("==========================================================")
