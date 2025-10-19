from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView
import sys

app = QApplication(sys.argv)

view = QWebEngineView()
view.setWindowTitle("Mascota Live2D")
view.load(QUrl.fromLocalFile("index.html"))  # carga el HTML local
view.setFixedSize(400, 400)  # tamaño base
view.show()

sys.exit(app.exec())
