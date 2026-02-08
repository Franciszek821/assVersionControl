import os
import sys

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from assvcPackage.reverse import reverse
from assvcPackage import stage, history


from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout, QHBoxLayout, QApplication, QFrame, QPushButton, QStyle, QListWidget, QListWidgetItem, QSplitter
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize, Qt
from assvcDestkopPackage import utils
from assvcDestkopPackage.loading import run_with_loading

class FileListItemWidget(QWidget):
    
    def __init__(self, file_path, status, icon_path, parent_window):
        super().__init__()
        self.file_path = file_path
        self.status = status

        self.parent_window = parent_window
        
        self.setStyleSheet("""
            QToolTip {
                color: #ffffff;
                background-color: #2a2a2a;
                border: 1px solid #4a4a4a;
                padding: 5px;
                border-radius: 3px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(5)
        

        inHistory = history.isPathInHistory(os.path.join(self.parent_window.repository_path, self.file_path))
        self.file_button = QPushButton()
        self.file_button.setText(file_path)
        self.file_button.setIcon(QIcon(icon_path))
        self.file_button.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 5px;
                    background: transparent;
                    border: none;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background: #3a3a3a;
                    border-radius: 3px;
                }
            """)
        if inHistory and status != "DELETED":
            self.file_button.clicked.connect(lambda: self.on_file_clicked())

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        pictures_dir = os.path.join(base_path, "pictures")
        
        self.open_button = QPushButton()
        open_path = os.path.join(pictures_dir, "goto_file_icon.png")
        self.open_button.setIcon(QIcon(open_path))
        self.open_button.setIconSize(QSize(16, 16))
        self.open_button.setToolTip("Open in file explorer")
        self.open_button.setStyleSheet("""
            QPushButton {
                max-width: 45px;
                min-height: 25px;
                font-size: 11px;
                opacity: 0;
                color: #ffffff;
                border-radius: 3px;
            }
            QPushButton:hover {
                background: #4a4a4a;
            }
        """)
        self.open_button.clicked.connect(lambda: self.on_open_clicked())
        
        self.stage_button = QPushButton()
        self.stage_path_plus = os.path.join(pictures_dir, "plus_icon.png")
        self.stage_path_minus = os.path.join(pictures_dir, "minus_icon.png")

        self.isStaged = stage.isStaged(os.path.join(self.parent_window.repository_path, self.file_path))
        if self.isStaged:
            self.stage_button.setIcon(QIcon(self.stage_path_minus))
            self.stage_button.setToolTip("Unstage file")
        else:
            self.stage_button.setIcon(QIcon(self.stage_path_plus))
            self.stage_button.setToolTip("Stage file")
        self.stage_button.setIconSize(QSize(16, 16))
        self.stage_button.setStyleSheet("""
            QPushButton {
                max-width: 45px;
                min-height: 25px;
                font-size: 11px;
                opacity: 0;
                color: #ffffff;
                border-radius: 3px;
            }
            QPushButton:hover {
                background: #4a4a4a;
            }
        """)
        self.stage_button.clicked.connect(lambda: self.on_stage_clicked())
        
        self.revert_button = QPushButton()
        revert_path = os.path.join(pictures_dir, "revert_icon.png")
        self.revert_button.setIcon(QIcon(revert_path))
        self.revert_button.setIconSize(QSize(16, 16))
        self.revert_button.setToolTip("Revert changes")
        self.revert_button.setStyleSheet("""
            QPushButton {
                max-width: 50px;
                min-height: 25px;
                font-size: 11px;
                opacity: 0;
                color: #ffffff;
                border-radius: 3px;
            }
            QPushButton:hover {
                background: #4a4a4a;
            }
        """)
        self.revert_button.clicked.connect(lambda: self.on_revert_clicked())
        
        layout.addWidget(self.file_button, 1)
        layout.addWidget(self.open_button)
        layout.addWidget(self.stage_button)
        layout.addWidget(self.revert_button)
    
    def on_file_clicked(self):
        print(f"File clicked: {self.file_path}")
        full_path = os.path.join(self.parent_window.repository_path, self.file_path)
        self.parent_window.show_diff(full_path, self.file_path)
        
    def on_open_clicked(self):
        print(f"Diff clicked for: {self.file_path}")
        full_path = os.path.join(self.parent_window.repository_path, self.file_path)
        utils.open_in_explorer_file(full_path)
        
    def on_stage_clicked(self):
        print(f"Stage clicked for: {self.file_path}")
        full_path = os.path.join(self.parent_window.repository_path, self.file_path)
        if self.isStaged:
            stage.unstage(full_path)
            self.isStaged = False
            self.stage_button.setIcon(QIcon(self.stage_path_plus))
            self.stage_button.setToolTip("Stage file")
            self.parent_window.on_refresh_clicked()
        else:
            stage.stage(full_path)
            self.isStaged = True
            self.stage_button.setIcon(QIcon(self.stage_path_minus))
            self.stage_button.setToolTip("Unstage file")
            self.parent_window.on_refresh_clicked()
        
    def on_revert_clicked(self):
        print(f"Revert clicked for: {self.file_path}")
        full_path = os.path.join(self.parent_window.repository_path, self.file_path)
        reverse(isPrintArgument=False, isForce=True, file_path=full_path)
        self.parent_window.on_refresh_clicked()
