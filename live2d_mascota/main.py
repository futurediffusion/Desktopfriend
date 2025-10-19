import sys
import os
from PySide6.QtCore import QUrl, Qt, QPoint, QAbstractNativeEventFilter
from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QPalette, QColor

IS_WINDOWS = sys.platform.startswith("win")

if IS_WINDOWS:
    import ctypes
    from ctypes import wintypes

    WM_MOUSEMOVE = 0x0200
    WM_INPUT = 0x00FF
    RIDEV_INPUTSINK = 0x00000100

    class MSG(ctypes.Structure):
        _fields_ = [
            ("hwnd", wintypes.HWND),
            ("message", wintypes.UINT),
            ("wParam", wintypes.WPARAM),
            ("lParam", wintypes.LPARAM),
            ("time", wintypes.DWORD),
            ("pt", wintypes.POINT),
        ]

    class RAWINPUTDEVICE(ctypes.Structure):
        _fields_ = [
            ("usUsagePage", wintypes.USHORT),
            ("usUsage", wintypes.USHORT),
            ("dwFlags", wintypes.DWORD),
            ("hwndTarget", wintypes.HWND),
        ]

    user32 = ctypes.windll.user32
    user32.GetCursorPos.argtypes = [ctypes.POINTER(wintypes.POINT)]
    user32.GetCursorPos.restype = wintypes.BOOL
    user32.RegisterRawInputDevices.argtypes = [
        ctypes.POINTER(RAWINPUTDEVICE),
        wintypes.UINT,
        wintypes.UINT,
    ]
    user32.RegisterRawInputDevices.restype = wintypes.BOOL


class GlobalMouseEventFilter(QAbstractNativeEventFilter if IS_WINDOWS else object):
    """Filtro nativo para capturar el movimiento global del mouse."""

    def __init__(self):
        if IS_WINDOWS:
            super().__init__()
        self._listeners = set()

    def add_listener(self, listener):
        self._listeners.add(listener)

    def remove_listener(self, listener):
        self._listeners.discard(listener)

    def nativeEventFilter(self, eventType, message):  # pragma: no cover - dependiente de SO
        if not IS_WINDOWS or eventType != "windows_generic_MSG":
            return False, 0

        msg = MSG.from_address(int(message))
        if msg.message == WM_INPUT:
            point = wintypes.POINT()
            if user32.GetCursorPos(ctypes.byref(point)):
                self._emit_point(point.x, point.y)
        elif msg.message == WM_MOUSEMOVE:
            self._emit_point(msg.pt.x, msg.pt.y)

        return False, 0

    def _emit_point(self, x, y):
        if not self._listeners:
            return

        point = QPoint(int(x), int(y))
        for listener in tuple(self._listeners):
            listener(point)

class TransparentLive2DWidget(QWebEngineView):
    """Ventana transparente siempre visible con Live2D"""

    def __init__(self, mouse_filter=None):
        super().__init__()
        self._mouse_filter = mouse_filter
        self._page_ready = False
        self._raw_input_registered = False
        self._last_global_point = None
        self.setupWindow()
        self.setupDragging()
        self._connectMouseFilter()
        self.page().loadFinished.connect(self._on_page_load_finished)
        self.loadLive2D()
    
    def setupWindow(self):
        """Configura ventana transparente y siempre visible"""
        # Sin bordes + siempre encima + fondo transparente
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |  # Sin bordes
            Qt.WindowType.WindowStaysOnTopHint |  # Siempre encima
            Qt.WindowType.Tool  # No aparece en barra de tareas
        )
        
        # Fondo transparente
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)
        self.setAutoFillBackground(False)
        if self.viewport() is not None:
            self.viewport().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.viewport().setAutoFillBackground(False)
            self.viewport().setStyleSheet("background: transparent;")
        self.setStyleSheet("background: transparent;")

        # Página transparente
        self.page().setBackgroundColor(QColor(0, 0, 0, 0))
        
        # Tamaño y posición inicial
        self.setFixedSize(400, 500)
        self.move(100, 100)  # Esquina superior izquierda
        
        self.setWindowTitle("🐾 Live2D Friend")
    
    def setupDragging(self):
        """Permite arrastrar la ventana"""
        self.dragging = False
        self.drag_candidate = False
        self.system_moving = False
        self.offset = QPoint()
        self.press_pos = QPoint()
        # Asegura que recibimos eventos de movimiento incluso si el contenido web
        # está capturando el puntero.
        self.setMouseTracking(True)

    def _connectMouseFilter(self):
        if self._mouse_filter is not None:
            self._mouse_filter.add_listener(self._handle_global_mouse_move)
            self.destroyed.connect(self._on_destroyed)
    
    def loadLive2D(self):
        """Carga el servidor Live2D"""
        # URL del servidor HTTP local
        url = QUrl("http://127.0.0.1:5500")
        self.load(url)

    def showEvent(self, event):
        super().showEvent(event)
        self._ensure_raw_input_registration()
    
    # ===== ARRASTRE DE VENTANA =====
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_candidate = True
            self.press_pos = event.globalPosition().toPoint()
            self.system_moving = False

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            if self.drag_candidate and not self.dragging:
                # Inicia el arrastre cuando la distancia es perceptible.
                if (event.globalPosition().toPoint() - self.press_pos).manhattanLength() >= 6:
                    window = self.windowHandle()
                    if window is not None and window.startSystemMove():
                        self.system_moving = True
                        self.drag_candidate = False
                        event.accept()
                        return

                    # Fallback manual si el movimiento nativo no existe.
                    self.dragging = True
                    self.drag_candidate = False
                    self.offset = self.press_pos - self.pos()
                    self.grabMouse()

            if self.dragging:
                self.move(event.globalPosition().toPoint() - self.offset)
                event.accept()
                return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            was_dragging = self.dragging or self.system_moving
            self.dragging = False
            self.drag_candidate = False
            self.system_moving = False
            if self.mouseGrabber() == self:
                self.releaseMouse()
            if was_dragging:
                event.accept()

        super().mouseReleaseEvent(event)

    def _on_destroyed(self, _=None):
        if self._mouse_filter is not None:
            self._mouse_filter.remove_listener(self._handle_global_mouse_move)

    def _on_page_load_finished(self, ok):
        self._page_ready = bool(ok)

    def _ensure_raw_input_registration(self):  # pragma: no cover - dependiente de SO
        if not IS_WINDOWS or self._raw_input_registered:
            return

        hwnd = int(self.winId())
        if not hwnd:
            return

        rid = RAWINPUTDEVICE()
        rid.usUsagePage = 0x01
        rid.usUsage = 0x02
        rid.dwFlags = RIDEV_INPUTSINK
        rid.hwndTarget = wintypes.HWND(hwnd)

        if user32.RegisterRawInputDevices(ctypes.byref(rid), 1, ctypes.sizeof(rid)):
            self._raw_input_registered = True
        else:
            error_code = ctypes.get_last_error()
            print(f"[Live2D] No se pudo registrar RAWINPUT (error {error_code})")

    def _handle_global_mouse_move(self, global_point):
        if not self._page_ready or not self.isVisible():
            return

        if self.dragging or self.system_moving:
            return

        coords = (global_point.x(), global_point.y())
        if self._last_global_point == coords:
            return

        self._last_global_point = coords

        local_point = self.mapFromGlobal(global_point)
        if self.rect().contains(local_point):
            # El contenido ya recibe eventos regulares del mouse.
            return

        self._dispatch_synthetic_mouse_event(local_point, global_point)

    def _dispatch_synthetic_mouse_event(self, local_point, global_point):
        if not self._page_ready:
            return

        local_x = int(local_point.x())
        local_y = int(local_point.y())
        global_x = int(global_point.x())
        global_y = int(global_point.y())

        script = (
            "(() => {"
            "const target = document.querySelector('canvas') || document.body;"
            "if (!target) return;"
            f"const evt = new MouseEvent('mousemove', {{bubbles: true, cancelable: true, clientX: {local_x}, clientY: {local_y}, screenX: {global_x}, screenY: {global_y}, buttons: 0}});"
            "target.dispatchEvent(evt);"
            "})();"
        )

        self.page().runJavaScript(script)


def main():
    """Inicia la aplicación"""
    app = QApplication(sys.argv)

    mouse_filter = None
    if IS_WINDOWS:
        mouse_filter = GlobalMouseEventFilter()
        app.installNativeEventFilter(mouse_filter)

    # Detectar si el servidor está corriendo
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_running = sock.connect_ex(('127.0.0.1', 5500)) == 0
    sock.close()
    
    if not server_running:
        print("\n⚠️  SERVIDOR NO DETECTADO")
        print("➡️  Ejecuta primero: serve_and_run.bat")
        print("    O manualmente: cd web && python -m http.server 5500\n")
        sys.exit(1)

    # Crear ventana
    window = TransparentLive2DWidget(mouse_filter)
    window.show()
    
    print("\n✅ Mascota Live2D activa")
    print("💡 Arrastra con el mouse para moverla")
    print("🔴 Cierra con Ctrl+C o la 'X' del navegador\n")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
