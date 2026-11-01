import sys
import os
import time
import glob
import json
import argparse
import socket
import threading
import ctypes
from PyQt6.QtCore import Qt, QTimer, QObject, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QGuiApplication, QPainter, QColor, QBrush

BRAIN_DIR = r"C:\Users\xanth\.gemini\antigravity-cli\brain"
GWL_EXSTYLE = -20
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOOLWINDOW = 0x00000080
HWND_TOPMOST = -1
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040

def make_topmost_transparent(hwnd):
    if sys.platform == 'win32':
        try:
            user32 = ctypes.windll.user32
            style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            style |= (WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW)
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
            user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW)
        except Exception as e:
            print(f"Win32 error: {e}", flush=True)

class ScreenLineWindow(QWidget):
    def __init__(self, screen_geometry, height=7):
        super().__init__()
        self.screen_geometry = screen_geometry
        self.line_height = height
        # Optimal Warm Vivid Gold (#FFB300)
        self.fill_color = QColor(255, 179, 0)
        self.is_active = False
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        y = screen_geometry.y() + screen_geometry.height() - self.line_height

        self.setGeometry(
            screen_geometry.x(),
            y,
            screen_geometry.width(),
            self.line_height
        )

    def showEvent(self, event):
        super().showEvent(event)
        make_topmost_transparent(int(self.winId()))

    def paintEvent(self, event):
        if self.is_active:
            painter = QPainter(self)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(self.fill_color))
            painter.drawRect(0, 0, self.width(), self.height())

    def set_color_state(self, state, opacity=0.92):
        self.setWindowOpacity(opacity)
        
        if state == "permission":
            # Balanced Warm Vivid Gold (#FFB300)
            self.fill_color = QColor(255, 179, 0)
            self.is_active = True
        elif state == "complete":
            # Vivid Mint Green (#00E676)
            self.fill_color = QColor(0, 230, 118)
            self.is_active = True
        elif state == "busy":
            # Sky Blue (#03A9F4)
            self.fill_color = QColor(3, 169, 244)
            self.is_active = True
        else:
            self.is_active = False

        self.update()
        
        if not self.is_active:
            self.hide()
        else:
            self.show()
            self.raise_()
            make_topmost_transparent(int(self.winId()))

class LogMonitorThread(QObject):
    state_changed = pyqtSignal(str)

    def __init__(self, interval=0.3):
        super().__init__()
        self.interval = interval
        self.running = True

    def start_monitoring(self):
        t = threading.Thread(target=self._monitor_loop, daemon=True)
        t.start()

    def _get_latest_transcript(self):
        if not os.path.exists(BRAIN_DIR):
            return None
        pattern = os.path.join(BRAIN_DIR, "*", ".system_generated", "logs", "transcript.jsonl")
        files = glob.glob(pattern)
        if not files:
            return None
        files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
        return files[0]

    def _analyze_transcript(self, filepath):
        if not filepath or not os.path.exists(filepath):
            return "off"
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
        except Exception:
            return "off"

        if not lines:
            return "off"

        parsed_steps = []
        for line in lines:
            try:
                parsed_steps.append(json.loads(line))
            except Exception:
                continue

        if not parsed_steps:
            return "off"

        last_user_input_idx = -1
        last_planner_idx = -1

        for idx, s in enumerate(parsed_steps):
            stype = s.get("type")
            if stype == "USER_INPUT":
                last_user_input_idx = idx
            elif stype == "PLANNER_RESPONSE":
                last_planner_idx = idx

        if last_planner_idx > last_user_input_idx:
            planner_step = parsed_steps[last_planner_idx]
            tool_calls = planner_step.get("tool_calls", [])
            for tc in tool_calls:
                name = tc.get("name", "")
                if name in ("ask_permission", "ask_question"):
                    return "permission"

            if last_planner_idx < len(parsed_steps) - 1:
                return "busy"
            else:
                return "complete" if not tool_calls else "busy"
        elif last_user_input_idx >= last_planner_idx:
            return "busy"

        return "off"

    def _monitor_loop(self):
        last_state = None
        while self.running:
            try:
                tf = self._get_latest_transcript()
                if tf:
                    state = self._analyze_transcript(tf)
                    if state != last_state:
                        self.state_changed.emit(state)
                        last_state = state
                time.sleep(self.interval)
            except Exception as e:
                time.sleep(self.interval)

class UDPReceiver(QObject):
    command_received = pyqtSignal(str)

    def __init__(self, port=9999):
        super().__init__()
        self.port = port
        self.running = True

    def start_listening(self):
        t = threading.Thread(target=self._listen_loop, daemon=True)
        t.start()

    def _listen_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("127.0.0.1", self.port))
        while self.running:
            try:
                data, _ = sock.recvfrom(1024)
                cmd = data.decode('utf-8').strip()
                self.command_received.emit(cmd)
            except Exception:
                pass

class IndicatorController(QObject):
    def __init__(self, app, line_height=7):
        super().__init__()
        self.app = app
        self.line_height = line_height
        self.windows = []
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.anim_tick = 0
        self.current_state = "off"
        
        self.init_windows()

    def init_windows(self):
        screens = QGuiApplication.screens()
        for s in screens:
            win_bottom = ScreenLineWindow(s.geometry(), height=self.line_height)
            self.windows.append(win_bottom)
        print(f"Initialized {len(self.windows)} bottom indicator lines across {len(screens)} screens.", flush=True)

    @pyqtSlot(str)
    def set_state(self, state):
        state = state.lower().strip()
        self.current_state = state
        self.anim_tick = 0
        
        if state in ("permission", "complete", "busy"):
            self.timer.start(40)
        else:
            self.timer.stop()

        for win in self.windows:
            win.set_color_state(state, opacity=0.92)

    def update_animation(self):
        self.anim_tick += 1
        
        if self.current_state == "permission":
            import math
            # Smooth pulse between 0.55 and 0.92
            val = 0.735 + 0.185 * math.sin(self.anim_tick * 0.2)
            for win in self.windows:
                win.set_color_state("permission", opacity=val)
                
        elif self.current_state == "complete":
            if self.anim_tick < 16:
                val = 0.92 if (self.anim_tick // 2) % 2 == 0 else 0.2
                for win in self.windows:
                    win.set_color_state("complete", opacity=val)
            else:
                for win in self.windows:
                    win.set_color_state("complete", opacity=0.92)
                if self.anim_tick > 200:
                    self.set_state("off")

        elif self.current_state == "busy":
            import math
            val = 0.5 + 0.4 * math.sin(self.anim_tick * 0.1)
            for win in self.windows:
                win.set_color_state("busy", opacity=val)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", choices=["permission", "complete", "busy", "off"], help="Run test state")
    parser.add_argument("--port", type=int, default=9999, help="UDP port")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    controller = IndicatorController(app)

    if args.test:
        controller.set_state(args.test)
    else:
        receiver = UDPReceiver(port=args.port)
        receiver.command_received.connect(controller.set_state)
        receiver.start_listening()
        
        log_mon = LogMonitorThread(interval=0.3)
        log_mon.state_changed.connect(controller.set_state)
        log_mon.start_monitoring()

    sys.exit(app.exec())
