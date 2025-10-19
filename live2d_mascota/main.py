import sys
import os
from PySide6.QtCore import QUrl, Qt, QPoint
from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QPalette, QColor

class TransparentLive2DWidget(QWebEngineView):
    """Ventana transparente siempre visible con Live2D"""
    
    def __init__(self):
        super().__init__()
        self.setupWindow()
        self.setupDragging()
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
    
    def loadLive2D(self):
        """Carga el servidor Live2D"""
        # URL del servidor HTTP local
        url = QUrl("http://127.0.0.1:5500")
        self.load(url)
    
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


def main():
    """Inicia la aplicación"""
    app = QApplication(sys.argv)
    
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
    window = TransparentLive2DWidget()
    window.show()
    
    print("\n✅ Mascota Live2D activa")
    print("💡 Arrastra con el mouse para moverla")
    print("🔴 Cierra con Ctrl+C o la 'X' del navegador\n")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
