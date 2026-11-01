# PyQt6 / Win32 最前面・クリック透過画面オーバーレイ開発ナレッジ (ガッツ鍛造)

## 鉄則ルール
Windows 上で全ディスプレイ対応の最前面・クリック透過ライン/ウィンドウを構築する際、透過レイヤー属性の競合による「100%透明化バグ」を回避する手法。

---

## 1. Win32 API 属性の指定
* **絶対遵守**: `WS_EX_LAYERED` (0x80000) を Win32 API の `SetWindowLongW` で勝手に後から付与してはならない。Qt の `setWindowOpacity` および描画エンジンと競合して完全不透過/不可視化の原因となる。
* **推奨属性**: `WS_EX_TRANSPARENT` (0x20) | `WS_EX_TOOLWINDOW` (0x80) のみを使用する。

```python
GWL_EXSTYLE = -20
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOOLWINDOW = 0x00000080
HWND_TOPMOST = -1

def make_topmost_transparent(hwnd):
    user32 = ctypes.windll.user32
    style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    style |= (WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW)
    user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
    user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW)
```

---

## 2. PyQt6 自前描画 (QPainter)
* `setStyleSheet("background-color: ...;")` に頼らず、`paintEvent` をオーバーライドして `QPainter.drawRect` で確実な純色を描画する。

```python
def paintEvent(self, event):
    if self.is_active:
        painter = QPainter(self)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.fill_color))
        painter.drawRect(0, 0, self.width(), self.height())
```
