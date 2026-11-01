import sys
import subprocess
import time
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Find pythonw.exe or python.exe
python_exe = sys.executable
pythonw_exe = python_exe.lower().replace("python.exe", "pythonw.exe")
if not os.path.exists(pythonw_exe):
    pythonw_exe = python_exe

def main():
    indicator_script = os.path.join(BASE_DIR, "indicator.py")
    monitor_script = os.path.join(BASE_DIR, "log_monitor.py")
    send_script = os.path.join(BASE_DIR, "send_state.py")

    print(f"Launching Antigravity Indicator GUI ({pythonw_exe})...")
    gui_proc = subprocess.Popen([pythonw_exe, indicator_script], cwd=BASE_DIR)
    
    time.sleep(1) # Wait for GUI socket initialization
    
    print(f"Launching Antigravity Log Monitor ({pythonw_exe})...")
    mon_proc = subprocess.Popen([pythonw_exe, monitor_script], cwd=BASE_DIR)

    print(f"Antigravity Indicator System Active! (GUI PID: {gui_proc.pid}, Monitor PID: {mon_proc.pid})")
    
    # Test flash (Green for system ready)
    subprocess.run([python_exe, send_script, "complete"])

if __name__ == "__main__":
    main()
