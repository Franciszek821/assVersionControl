import os
import sys

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from assvcDestkopPackage import menu, utils


from PySide6.QtWidgets import (
    QMainWindow, QLabel, QWidget,
    QVBoxLayout, QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ASSVC Desktop")
        self.resize(800, 600)
        self.selected_folder = None

        self.setStyleSheet("""
            QMainWindow {
                background: #1a1a1a;
            }
        """)

        self.child_windows = []
        self.create_ui()

    def create_ui(self):
        self.create_title()
        self.create_buttons()
        self.create_menu()
        
    def create_menu(self):
        menubar = self.menuBar()
        menu.home_menu(self, menubar)
        menu.file_menu(self, menubar)
        menu.help_menu(self, menubar)

    def create_title(self):
        self.title = QLabel("ASSVC Desktop")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("""
            QLabel {
                font-size: 48px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #ffffff;
                padding: 30px;
            }
        """)

    def create_buttons(self):
        import_button = QPushButton("Import Repository")
        new_button = QPushButton("New Repository")
        open_button = QPushButton("Open Repository")

        import_button.clicked.connect(lambda: utils.import_repository(self))
        new_button.clicked.connect(lambda: utils.new_repository(self))
        open_button.clicked.connect(lambda: utils.open_folder(self))

        button_style = """
            QPushButton {
                min-width: 200px;
                min-height: 70px;
                font-size: 18px;
                font-weight: bold;
                color: #ffffff;
                background: #2a2a2a;
                border-radius: 12px;
            }
            QPushButton:hover {
                background: #3a3a3a;
            }
        """

        for b in (import_button, new_button, open_button):
            b.setStyleSheet(button_style)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addStretch()
        layout.addWidget(self.title)

        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(import_button)
        buttons.addWidget(new_button)
        buttons.addWidget(open_button)
        buttons.addStretch()

        layout.addLayout(buttons)
        layout.addStretch()

        self.setCentralWidget(central)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
