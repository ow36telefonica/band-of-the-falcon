import sys
import time
import os
import glob
import json
import socket
import argparse

UDP_PORT = 9999
BRAIN_DIR = r"C:\Users\xanth\.gemini\antigravity-cli\brain"

def send_udp_command(cmd, port=UDP_PORT):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(cmd.encode('utf-8'), ("127.0.0.1", port))
    except Exception as e:
        print(f"Failed to send UDP command: {e}")

def get_latest_transcript_file():
    if not os.path.exists(BRAIN_DIR):
        return None
    
    # Find all transcript.jsonl files
    pattern = os.path.join(BRAIN_DIR, "*", ".system_generated", "logs", "transcript.jsonl")
    files = glob.glob(pattern)
    if not files:
        return None
    
    # Sort by modification time (most recent first)
    files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
    return files[0]

def analyze_transcript(filepath):
    """
    Parses transcript.jsonl to determine current state.
    Returns: 'permission', 'complete', 'busy', or 'off'
    """
    if not filepath or not os.path.exists(filepath):
        return "off"

    lines = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading transcript: {e}")
        return "off"

    if not lines:
        return "off"

    # Inspect from recent steps backwards
    last_user_input_idx = -1
    last_planner_idx = -1
    last_step = None

    parsed_steps = []
    for line in lines:
        try:
            parsed_steps.append(json.loads(line))
        except Exception:
            continue

    if not parsed_steps:
        return "off"

    last_step = parsed_steps[-1]

    # Find last USER_INPUT and last PLANNER_RESPONSE
    for idx, s in enumerate(parsed_steps):
        stype = s.get("type")
        if stype == "USER_INPUT":
            last_user_input_idx = idx
        elif stype == "PLANNER_RESPONSE":
            last_planner_idx = idx

    # If planner responded after the last user input
    if last_planner_idx > last_user_input_idx:
        planner_step = parsed_steps[last_planner_idx]
        tool_calls = planner_step.get("tool_calls", [])
        
        # Check if asking for permission or question
        for tc in tool_calls:
            name = tc.get("name", "")
            if name in ("ask_permission", "ask_question"):
                return "permission"

        # Check if the subsequent steps are running tools
        if last_planner_idx < len(parsed_steps) - 1:
            # There are follow-up tool execution steps
            following = parsed_steps[last_planner_idx + 1:]
            for fs in following:
                if fs.get("status") == "RUNNING":
                    return "busy"
            
            # If all tool calls ended and no new PLANNER_RESPONSE yet
            return "busy"
        else:
            # Planner response is the very last step and has no tool calls -> Task Complete!
            if not tool_calls:
                return "complete"
            else:
                return "busy"
    
    # If user input is waiting for planner response
    elif last_user_input_idx >= last_planner_idx:
        return "busy"

    return "off"

def monitor_loop(interval=1.0, port=UDP_PORT):
    print("Starting Antigravity Log Monitor...")
    last_state = None
    last_file = None

    while True:
        try:
            transcript_file = get_latest_transcript_file()
            if transcript_file:
                state = analyze_transcript(transcript_file)
                if state != last_state:
                    print(f"[State Change] {last_state} -> {state} (File: {os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(transcript_file))))})")
                    send_udp_command(state, port)
                    last_state = state
            time.sleep(interval)
        except KeyboardInterrupt:
            print("Monitor stopped.")
            break
        except Exception as e:
            print(f"Monitor error: {e}")
            time.sleep(interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=float, default=0.5, help="Monitor check interval in seconds")
    parser.add_argument("--port", type=int, default=UDP_PORT, help="UDP port")
    args = parser.parse_args()

    monitor_loop(interval=args.interval, port=args.port)
