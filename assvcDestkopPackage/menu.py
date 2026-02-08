import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from assvcDestkopPackage import utils



from PySide6.QtWidgets import QApplication, QStyle
from PySide6.QtGui import QAction, QDesktopServices
from PySide6.QtCore import QUrl


def home_menu(parent, menubar):
    home_action = QAction("Home", parent, triggered=lambda: utils.return_to_main(parent))
    menubar.addAction(home_action)

def file_menu(parent, menubar, child_window=False, path=None):
    file_menu = menubar.addMenu("File")

    new_action = QAction(
        QApplication.style().standardIcon(QStyle.SP_FileIcon), 
        "New", 
        parent, 
        triggered=lambda: utils.new_repository(parent)
    )
    new_action.setShortcut("F1")
    file_menu.addAction(new_action)
        
    open_action = QAction(
        QApplication.style().standardIcon(QStyle.SP_DirOpenIcon), 
        "Open", 
        parent, 
        triggered=lambda: utils.open_folder(parent)
    )
    open_action.setShortcut("F2")
    file_menu.addAction(open_action)

    if child_window:
        open_in_explorer_action = QAction(
            QApplication.style().standardIcon(QStyle.SP_DirIcon), 
            "Open in Explorer", 
            parent, 
            triggered=lambda: utils.open_in_explorer(path)
        )
        file_menu.addAction(open_in_explorer_action)
        open_in_explorer_action.setShortcut("F3")

def repository_menu(parent, menubar, path=None):
    repository_menu = menubar.addMenu("Repository")

    import_action = QAction(
        QApplication.style().standardIcon(QStyle.SP_DialogOpenButton), 
        "Import", 
        parent, 
        triggered=lambda: utils.import_repository(parent)
    )
    repository_menu.addAction(import_action)
    import_action.setShortcut("F4")

    export_action = QAction(
        QApplication.style().standardIcon(QStyle.SP_DialogSaveButton), 
        "Export", 
        parent, 
        triggered=lambda: utils.export_repository(path, parent)
    )
    repository_menu.addAction(export_action)
    export_action.setShortcut("F5")


def help_menu(parent, menubar):
    help_menu = menubar.addMenu("Help")

    help_action = QAction(
        QApplication.style().standardIcon(QStyle.SP_DialogHelpButton), 
        "Help", 
        parent
    )
    help_action.setShortcut("F6")
    help_action.triggered.connect(
        lambda: QDesktopServices.openUrl(
            QUrl("https://github.com/Franciszek821/assVersionControl/blob/main/README.md")
        )
    )

    about_action = QAction(
        QApplication.style().standardIcon(QStyle.SP_MessageBoxInformation), 
        "About", 
        parent
    )
    about_action.setShortcut("F7")
    about_action.triggered.connect(
        lambda: QDesktopServices.openUrl(
            QUrl("https://github.com/Franciszek821/assVersionControl")
        )
    )
        
    help_menu.addAction(help_action)
    help_menu.addAction(about_action)
