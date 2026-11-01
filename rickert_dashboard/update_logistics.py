# -*- coding: utf-8 -*-
import os
import json
import re
import time
import requests
from datetime import datetime, timedelta
import hashlib

WORKSPACE_DIR = r"C:\Users\xanth\Dropbox\個人請負\品川区テニス連盟\hp\docs\rickert_dashboard"
OUTPUT_JS_PATH = os.path.join(WORKSPACE_DIR, "logistics_data.js")

TOKEN_LIMIT = 20000000
REQ_LIMIT = 1000
GITHUB_REPO = "ow36telefonica/shinagawa-tennis-a"
GH_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs"

last_gh_check = 0
gh_status_cache = None

LAST_FILE_PATH, LAST_FILE_POS = None, 0
roster, total_tokens, total_requests, comm_logs, last_api_total = {}, 0, 0, [], 0
proposals = []
parsed_request_ids = set()
IS_ONCE_MODE = False

ID_NAME_MAP = {
    "strategist-griffith": "ガストン", "gaston-strategist": "ガストン",
    "modernizer-guts": "ガッツ", "guts-modernizer": "ガッツ",
    "validator-casca": "コルカス", "corkus-validator": "コルカス",
    "checker-judeau": "ジュドー", "judeau-checker": "ジュドー",
    "pippin-git": "ピピン", "pippin-transporter": "ピピン",
    "erica-blacksmith": "エリカ",
    "farnese-chronicler": "ファルネーゼ"
}

last_sheet_check = 0
SHEET_URL = "https://docs.google.com/spreadsheets/d/1uR33VUcSIVwLNz5eKbgo5K6bTc8Tty_Lhq5KVCUkx4o/export?format=csv"
HASH_FILE = r"C:\Users\xanth\.gemini\antigravity-cli\scratch\sheet_hash.txt"
NOTIFICATION_FILE = r"C:\Users\xanth\.gemini\antigravity-cli\scratch\sheet_notifications.json"

def check_sheet_updates():
    global last_sheet_check
    now = time.time()
    if now - last_sheet_check < 60:
        return []
    last_sheet_check = now
    
    try:
        res = requests.get(SHEET_URL, timeout=10)
        if res.status_code != 200:
            return []
        content = res.content
        now_hash = hashlib.md5(content).hexdigest()
    except Exception:
        return []
        
    prev_hash = ""
    if os.path.exists(HASH_FILE):
        try:
            with open(HASH_FILE, 'r', encoding='utf-8') as f:
                prev_hash = f.read().strip()
        except:
            pass
            
    notifications = []
    if prev_hash and now_hash != prev_hash:
        timestamp = datetime.now().strftime('%m/%d %H:%M:%S')
        try:
            lines = content.decode('utf-8').split('\n')
            valid_lines = [l for l in lines if l.strip()]
            num_rows = len(valid_lines)
            
            msg = "<strong>【警報】ピピン: 依頼管理表（Google Sheets）の更新を検知しました。新たな任務が追加・変更された可能性があります。</strong>"
            embed = f"シート全体のハッシュ値が変更されました（現在の行数: {num_rows}）"
            
            new_notif = {
                "sender": "casca",
                "name": "ピピン",
                "avatar": "assets/avatars/pippin.png",
                "time": timestamp,
                "body": msg,
                "embed": embed
            }
            notifications.append(new_notif)
            
            saved_notifs = []
            if os.path.exists(NOTIFICATION_FILE):
                try:
                    with open(NOTIFICATION_FILE, 'r', encoding='utf-8') as f:
                        saved_notifs = json.load(f)
                except:
                    pass
            saved_notifs.append(new_notif)
            saved_notifs = saved_notifs[-20:]
            with open(NOTIFICATION_FILE, 'w', encoding='utf-8') as f:
                json.dump(saved_notifs, f, ensure_ascii=False, indent=4)
        except Exception:
            pass
            
    try:
        with open(HASH_FILE, 'w', encoding='utf-8') as f:
            f.write(now_hash)
    except:
        pass
        
    return notifications

def get_gh_actions_status():
    global last_gh_check, gh_status_cache
    now = time.time()
    if now - last_gh_check < 60 and gh_status_cache:
        return gh_status_cache
    try:
        response = requests.get(GH_API_URL, timeout=10)
        if response.status_code == 200:
            runs = response.json().get("workflow_runs", [])
            if runs:
                latest = runs[0]
                gh_status_cache = {"status": latest.get("status"), "conclusion": latest.get("conclusion"), "html_url": latest.get("html_url"), "updated_at": latest.get("updated_at")}
                last_gh_check = now
                return gh_status_cache
    except: pass
    return gh_status_cache

def get_proposals_from_md():
    md_proposals = []
    task_dirs = [
        r"C:\Users\xanth\docs\task_management",
        r"C:\Users\xanth\Dropbox\個人請負\品川区テニス連盟\hp\docs\rickert_dashboard"
    ]
    header_re = re.compile(r'^##\s*(?:\d+\.?\s+)?(.*?)\s*[（(](.*?)[）)]', re.MULTILINE)
    seen_files = set()
    for task_dir in task_dirs:
        if not os.path.exists(task_dir): continue
        for filename in os.listdir(task_dir):
            if filename.startswith("proposals_") and filename.endswith(".md") and filename not in seen_files:
                seen_files.add(filename)
                file_path = os.path.join(task_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    matches = list(header_re.finditer(content))
                    for i, match in enumerate(matches):
                        title, proposer_name = match.group(1).strip(), match.group(2).strip()
                        start_pos, end_pos = match.end(), matches[i+1].start() if i + 1 < len(matches) else len(content)
                        section_body = content[start_pos:end_pos].strip()
                        desc, status = "", "new"
                        for line in section_body.split('\n'):
                            clean_line = line.strip()
                            if '**提案内容**:' in clean_line: desc = clean_line.split('**提案内容**:', 1)[1].strip()
                            elif '**ステータス**:' in clean_line:
                                st_text = clean_line.split('**ステータス**:', 1)[1].strip()
                                if "未対応" in st_text: status = "pending"
                                elif "完了" in st_text or "済み" in st_text: status = "done"
                        proposer_id = "c"
                        for k, v in ID_NAME_MAP.items():
                            if v == proposer_name:
                                base_role = k.split('-')[0]
                                mapping = {"strategist": "gs", "gaston": "gs", "modernizer": "gt", "guts": "gt", "validator": "co", "corkus": "co", "casca": "c", "checker": "j", "judeau": "j", "pippin": "p", "transporter": "p", "blacksmith": "er", "erica": "er"}
                                proposer_id = mapping.get(base_role, base_role[:2])
                                break
                        md_proposals.append({"id": f"md_{filename}_{i}", "proposer": proposer_id.lower(), "title": title, "desc": desc, "status": status, "source": filename})
            except: pass
    return md_proposals

def get_daily_logs():
    log_dir = r"C:\Users\xanth"
    logs = []
    if not os.path.exists(log_dir): return logs
    log_re = re.compile(r'^(\d{8})-log\.md$')
    log_files = []
    for filename in os.listdir(log_dir):
        match = log_re.match(filename)
        if match: log_files.append((match.group(1), os.path.join(log_dir, filename), filename))
    log_files.sort(key=lambda x: x[0], reverse=True)
    for date_str, path, name in log_files[:10]:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                summary = ""
                summary_match = re.search(r'## セッション概要\n(.*?)(?=\n##|$)', content, re.DOTALL)
                if summary_match: summary = summary_match.group(1).strip()
                logs.append({"date": f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}", "filename": name, "summary": summary, "content": content})
        except: pass
    return logs

def get_transcript_path():
    base_dirs = [r"C:\Users\xanth\.gemini\tmp\xanth\chats", r"C:\Users\xanth\.gemini\antigravity-cli\brain", r"C:\Users\xanth\.gemini\antigravity\brain"]
    latest_time, latest_path = 0, None
    for base_dir in base_dirs:
        if not os.path.exists(base_dir): continue
        for root, dirs, files in os.walk(base_dir):
            for f in files:
                if f.endswith(".jsonl"):
                    t_path = os.path.join(root, f); mtime = os.path.getmtime(t_path)
                    if mtime > latest_time: latest_time, latest_path = mtime, t_path
    return latest_path

def censor_secrets(text):
    if not text: return ""
    patterns = [(r'sk-[a-zA-Z0-9]{32,}', '[REDACTED]'), (r'AIzaSy[a-zA-Z0-9-_]{33}', '[REDACTED]')]
    res = str(text)
    for p, r in patterns: res = re.sub(p, r, res)
    return res

def analyze_transcript():
    global LAST_FILE_PATH, LAST_FILE_POS, roster, total_tokens, total_requests, comm_logs, last_api_total, proposals, parsed_request_ids, IS_ONCE_MODE

    transcript_path = get_transcript_path()
    if not transcript_path: return

    LAST_FILE_POS = 0
    LAST_FILE_PATH = transcript_path
    roster = {
            "G": {"name": "グリフィス団長", "role": "最高責任者", "avatar": "assets/avatars/griffith.png", "status": "standby", "tokensUsed": 0, "reqsUsed": 0, "activeFile": "", "activeTask": "全軍指揮・軍命発令"},
            "C": {"name": "キャスカ", "role": "千人長 (司令塔)", "avatar": "assets/avatars/casca.png", "status": "working", "tokensUsed": 0, "reqsUsed": 0, "activeFile": "", "activeTask": "戦況把握・全軍統括"},
            "Gs": {"name": "ガストン", "role": "解析・計画", "avatar": "assets/avatars/gaston.png", "status": "standby", "tokensUsed": 0, "reqsUsed": 0, "activeFile": "", "activeTask": "戦術解析・計画立案"},
            "Gt": {"name": "ガッツ", "role": "実行・修正", "avatar": "assets/avatars/guts.png", "status": "standby", "tokensUsed": 0, "reqsUsed": 0, "activeFile": "", "activeTask": "ソース改修・切込実行"},
            "Co": {"name": "コルカス", "role": "検証・軍規", "avatar": "assets/avatars/corkus.png", "status": "standby", "tokensUsed": 0, "reqsUsed": 0, "activeFile": "", "activeTask": "内部検証・軍規チェック"},
            "P": {"name": "ピピン", "role": "輸送・デプロイ", "avatar": "assets/avatars/pippin.png", "status": "standby", "tokensUsed": 0, "reqsUsed": 0, "activeFile": "", "isBranded": False, "hasAmulet": True, "activeTask": "Git輸送・本番デプロイ"},
            "J": {"name": "ジュドー", "role": "偵察・外検", "avatar": "assets/avatars/judeau.png", "status": "standby", "tokensUsed": 0, "reqsUsed": 0, "activeFile": "", "activeTask": "外部検証・構造自動点検"},
            "Er": {"name": "エリカ", "role": "司令室保守", "avatar": "assets/avatars/erica.png", "status": "standby", "tokensUsed": 0, "reqsUsed": 0, "activeFile": "", "activeTask": "ダッシュボード・UI改修"},
            "Fa": {"name": "ファルネーゼ", "role": "記録・代筆", "avatar": "assets/avatars/farnese.png", "status": "standby", "tokensUsed": 0, "reqsUsed": 0, "activeFile": "", "activeTask": "戦記執筆・広報ドラフト"}
        }
    total_tokens, total_requests, comm_logs, last_api_total, proposals = 0, 0, [], 0, []
    parsed_request_ids = set()
    active_ai_model = "Gemini 3.8 Flash (High)"

    for k, v in roster.items():
        if "activeTask" not in v:
            default_tasks = {
                "G": "全軍指揮・軍命発令", "C": "戦況把握・全軍統括", "Gs": "戦術解析・計画立案",
                "Gt": "ソース改修・切込実行", "Co": "内部検証・8行軍規監視", "P": "Git本陣輸送・デプロイ",
                "J": "構造・レイアウト自動外検", "Er": "ダッシュボード・UI改修"
            }
            v["activeTask"] = default_tasks.get(k, "待機中")

    new_lines_parsed = False
    last_active_member = "C"

    with open(transcript_path, 'r', encoding='utf-8', errors='replace') as f:
        if LAST_FILE_POS > 0: f.seek(LAST_FILE_POS)
        for line in f:
            if not line.strip(): continue
            try: step = json.loads(line)
            except: continue
            if "$set" in step: continue
            new_lines_parsed = True
            
            step_id = step.get("step_index", "")
            step_type = step.get("type", "")
            step_source = step.get("source", "")
            content_data = step.get("content", "")
            
            if isinstance(content_data, str) and "Model Selection" in content_data:
                m_model = re.search(r'changed setting `?Model Selection`? from .*? to ([^\r\n]+?)\.(?:\s*No need to|\s*$)', content_data)
                if m_model:
                    active_ai_model = m_model.group(1).strip()
            
            created_at_raw = step.get("created_at") or step.get("timestamp", "")
            time_str = (datetime.fromisoformat(created_at_raw.replace('Z', '')) + timedelta(hours=9)).strftime('%m/%d %H:%M:%S') if created_at_raw else ""
            
            # Estimate token usage since it's not present in the logs
            inc = 0
            if step_source == "MODEL" and step_type == "PLANNER_RESPONSE" and step_id not in parsed_request_ids:
                total_requests += 1
                parsed_request_ids.add(step_id)
                inc = 5000 + len(str(content_data)) * 3
                total_tokens += inc
                
            content = "".join([c.get("text", "") for c in content_data if isinstance(c, dict)]) if isinstance(content_data, list) else str(content_data)
            tool_calls = step.get("tool_calls") or step.get("toolCalls", [])
            assigned_member, action_desc, action_embed = "C", "", ""
            
            if step_type == "USER_INPUT" or step_source == "USER_EXPLICIT":
                assigned_member = "G"
                clean_content = re.sub(r'<ADDITIONAL_METADATA>.*?</ADDITIONAL_METADATA>', '', content, flags=re.DOTALL).strip()
                if clean_content: comm_logs.append({"sender": "agent", "name": "グリフィス団長", "avatar": roster["G"]["avatar"], "time": time_str, "body": censor_secrets(clean_content)})
                continue
                
            if tool_calls:
                for tool in tool_calls:
                    name, args = tool.get("name", ""), tool.get("args", {})
                    if isinstance(args, str):
                        try: args = json.loads(args)
                        except: pass
                    
                    if name == "invoke_subagent":
                        target_id = args.get("TypeName", "団員")
                        invoked_name = ID_NAME_MAP.get(target_id, target_id)
                        action_desc = f"ガストン: 設計書に基づき、{invoked_name}への軍命伝達を仲介する。" if "strategist" in target_id else f"キャスカ: {invoked_name}へ軍命を伝達する。"
                        action_embed = f"【軍令の内容】\n{args.get('Prompt', '（命令書なし）')}"
                        roster[assigned_member]["activeTask"] = f"{invoked_name}への軍令伝達"
                    elif name == "write_to_file":
                        fpath = args.get('TargetFile','')
                        if "rickert_dashboard" in fpath: assigned_member, action_desc = "Er", f"エリカ: 司令室の設備（{os.path.basename(fpath)}）を新しく作り直したわ。"
                        else: assigned_member, action_desc = "Gt", f"ガッツ: 新兵器（{os.path.basename(fpath)}）の新規鍛造を完了したぜ。"
                        roster[assigned_member]["activeTask"] = f"新規作成: {os.path.basename(fpath)}"
                    elif name in ["replace_file_content", "multi_replace_file_content"]:
                        fpath = args.get('TargetFile','')
                        if "rickert_dashboard" in fpath: assigned_member, action_desc = "Er", f"エリカ: 司令室の調度品（{os.path.basename(fpath)}）をピカピカに磨いておいたよ！"
                        else: assigned_member, action_desc = "Gt", f"ガッツ: 刃（{os.path.basename(fpath)}）の研磨が済んだ。切れ味は最高だ。"
                        roster[assigned_member]["activeTask"] = f"コード改修: {os.path.basename(fpath)}"
                    elif name == "view_file":
                        fpath = args.get('AbsolutePath','')
                        if "rickert_dashboard" in fpath: assigned_member, action_desc = "Er", f"エリカ: 司令室の図面（{os.path.basename(fpath)}）を確認したよ。異常なし！"
                        else: assigned_member, action_desc = "Co", f"コルカス: 機密文書を検分した。ゴミ一つ見逃しちゃいねえよ。"
                        roster[assigned_member]["activeTask"] = f"検分・査察: {os.path.basename(fpath)}"
                    elif name == "run_command":
                        cmd = args.get("CommandLine", "")
                        assigned_member = "P"
                        if "git push" in cmd:
                            action_desc = "ピピン: 本陣（GitHub）への兵站輸送、完了した。"
                            roster["P"]["activeTask"] = "Git本陣輸送・デプロイ"
                        elif "update_logistics.py" in cmd:
                            assigned_member, action_desc = "Er", "エリカ: 監視網（リッケルト）の火加減を調整したよ。これでバッチリ！"
                            roster["Er"]["activeTask"] = "リッケルト監視網・UI保守"
                        elif "playwright" in cmd or "rule_checker" in cmd or "verify" in cmd:
                            assigned_member, action_desc = "J", "ジュドー: 千里眼での偵察完了。外陣に異常はないよ。"
                            roster["J"]["activeTask"] = "構造・レイアウト自動外検"
                        else:
                            action_desc = "ピピン: 特殊工作（コマンド実行）を遂行した。"
                            roster["P"]["activeTask"] = "特殊工作コマンド実行"
                        action_embed = f"【工作内容】\n> {cmd[:150]}"
                    elif name in ["search_web", "read_url_content", "read_browser_page"]:
                        assigned_member, action_desc = "J", "ジュドー: 外界（Web）の情報を拾い集めてきたよ。役に立つはずだ。"
                        roster["J"]["activeTask"] = "外界Web情報偵察"
                    
            roster[assigned_member]["tokensUsed"] += inc
            if inc > 0: roster[assigned_member]["reqsUsed"] += 1
            last_active_member = assigned_member
            if step_type == "PLANNER_RESPONSE" and content:
                for p_match in re.finditer(r'(?:^|\n)【改善提案】(.*?)(?=\n||$)'.replace('()', '(?:^|\n)【改善提案】(.*?)(?=\n|【|$)'), content):
                    # We can simplify this pattern to avoid issues
                    pass
                # Let's clean up and fix the regex match
                p_text_matches = re.finditer(r'(?:^|\n)【改善提案】(.*?)(?=\n|【|$)', content)
                for p_match in p_text_matches:
                    p_text = p_match.group(1).strip()
                    if p_text and not any(x in p_text for x in ["という形式", "例：", "説明のため"]):
                        if not any(p['desc'] == p_text for p in proposals): proposals.append({"id": f"prop_{len(proposals)}", "proposer": assigned_member.lower(), "title": p_text[:40] + "...", "desc": p_text, "impact": "戦力増強", "status": "new"})
                if "【任務開始】" in content:
                    decl_match = re.search(r'【任務開始】.*?(?=\n|$)', content)
                    decl = decl_match.group(0) if decl_match else "【任務開始】出撃する！"
                    comm_logs.append({"sender": "casca", "name": roster[assigned_member]['name'], "avatar": roster[assigned_member]["avatar"], "time": time_str, "body": f"<strong>{censor_secrets(decl)}</strong>", "embed": "🚨 団員が戦場へ投入されました"})
                else:
                    body_text = censor_secrets(content.strip())
                    if len(body_text) > 250: body_text = body_text[:250] + " ... (以下省略)"
                    comm_logs.append({"sender": "casca", "name": roster[assigned_member]['name'], "avatar": roster[assigned_member]["avatar"], "time": time_str, "body": body_text})
            if action_desc:
                embed_text = censor_secrets(action_embed) if action_embed else f"消費兵站: +{inc:,} tkn"
                if len(embed_text) > 200: embed_text = embed_text[:200] + "..."
                comm_logs.append({"sender": "casca", "name": roster[assigned_member]['name'], "avatar": roster[assigned_member]["avatar"], "time": time_str, "body": f"<strong>{action_desc}</strong>", "embed": embed_text})
        LAST_FILE_POS = f.tell()

    if "P" in roster:
        roster["P"]["isBranded"] = False
        roster["P"]["hasAmulet"] = True

    if new_lines_parsed or not os.path.exists(OUTPUT_JS_PATH) or IS_ONCE_MODE:
        for m_id, m in roster.items(): m["status"] = "working" if m_id == last_active_member else ("done" if m["tokensUsed"] > 0 else "standby")
        
        md_props = get_proposals_from_md()
        final_props = []
        md_descs = [p['desc'] for p in md_props]
        for p in proposals:
            if p['desc'] not in md_descs: final_props.append(p)
        final_props.extend(md_props)
        
        dlogs = get_daily_logs()
        
        # スプレッドシート更新通知をマージ
        check_sheet_updates()
        saved_notifs = []
        if os.path.exists(NOTIFICATION_FILE):
            try:
                with open(NOTIFICATION_FILE, 'r', encoding='utf-8') as f:
                    saved_notifs = json.load(f)
            except:
                pass
        
        merged_logs = list(comm_logs)
        for sn in saved_notifs:
            if not any(x.get('time') == sn.get('time') and x.get('body') == sn.get('body') for x in merged_logs):
                merged_logs.append(sn)
        
        try:
            merged_logs.sort(key=lambda x: x.get('time', ''))
        except:
            pass

        default_task_map = {
            "グリフィス団長": "全軍指揮・軍命発令", "キャスカ": "戦況把握・全軍統括", "ガストン": "戦術解析・計画立案",
            "ガッツ": "ソース改修・切込実行", "コルカス": "内部検証・8行軍規監視", "ピピン": "Git本陣輸送・デプロイ",
            "ジュドー": "構造・レイアウト自動外検", "エリカ": "ダッシュボード・UI改修", "ファルネーゼ": "戦記執筆・広報ドラフト"
        }
        roster_list = []
        for k, m in roster.items():
            task_str = m.get("activeTask") if m.get("activeTask") else default_task_map.get(m.get("name"), "待機中・次回出撃準備")
            item = {
                "name": m.get("name"),
                "role": m.get("role"),
                "avatar": m.get("avatar"),
                "status": m.get("status"),
                "tokensUsed": m.get("tokensUsed", 0),
                "reqsUsed": m.get("reqsUsed", 0),
                "activeFile": m.get("activeFile", ""),
                "activeTask": task_str
            }
            if "ピピン" in m.get("name", ""):
                item["isBranded"] = False
                item["hasAmulet"] = True
            roster_list.append(item)

        output_data = {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "active_model": active_ai_model,
            "total_tokens": total_tokens, "token_limit": TOKEN_LIMIT, "token_fill": round(min(100.0, (total_tokens / TOKEN_LIMIT) * 100), 2),
            "total_requests": total_requests, "req_limit": REQ_LIMIT, "req_fill": round(min(100.0, (total_requests / REQ_LIMIT) * 100), 2),
            "weekly_left": max(0, 100 - int(total_tokens / TOKEN_LIMIT * 80)),
            "roster": roster_list, "comm_logs": merged_logs,
            "proposals": final_props,
            "daily_logs": dlogs,
            "gh_actions": get_gh_actions_status()
        }
        with open(OUTPUT_JS_PATH, 'w', encoding='utf-8') as f:
            f.write("window.RICKERT_DATA = "); json.dump(output_data, f, ensure_ascii=False, indent=4); f.write(";")

        # --- 自動エクスポート機能 (Markdown) ---
        try:
            today_str = datetime.now().strftime('%Y%m%d')
            log_dir = os.path.join(WORKSPACE_DIR, "log")
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            md_path = os.path.join(log_dir, f"tactical_log_{today_str}.md")
            
            md_content = f"# 🦅 鷹の団 戦況通信ログ ({datetime.now().strftime('%Y-%m-%d')})\n\n"
            md_content += "## 📊 現在の兵站サマリー\n"
            md_content += f"- **総トークン消費**: {total_tokens:,} / {TOKEN_LIMIT:,} ({output_data['token_fill']}%)\n"
            md_content += f"- **総リクエスト数**: {total_requests:,} / {REQ_LIMIT:,} 回\n"
            md_content += f"- **最終更新**: {output_data['timestamp']}\n\n"
            md_content += "---\n\n"
            md_content += "## ⚔️ 通信記録 (Tactical Logs)\n"
            
            for l in comm_logs:
                # HTMLタグの除去とMarkdown装飾の調整
                body_clean = re.sub(r'<[^>]*>?', '', l['body'])
                md_content += f"- [{l['time']}] **{l['name']}**: {body_clean}\n"
                if 'embed' in l and l['embed']:
                    embed_clean = re.sub(r'<[^>]*>?', '', l['embed']).replace('\n', '\n  > ')
                    md_content += f"  > {embed_clean}\n"
            
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
        except Exception as e:
            print(f"Export Error: {e}")

if __name__ == "__main__":
    import sys
    IS_ONCE_MODE = "--once" in sys.argv
    print(f"Rickert Monitor Active. (Mode: {'Once' if IS_ONCE_MODE else 'Loop'})")
    while True:
        try:
            transcript_path = get_transcript_path()
            if transcript_path:
                analyze_transcript()
                print(f"Update complete: {datetime.now().strftime('%H:%M:%S')}")
            else: print("No transcript found.")
        except Exception as e: print(f"Error: {e}")
        if IS_ONCE_MODE: break
        time.sleep(3)
