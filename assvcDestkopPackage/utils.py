import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from assvcPackage.start import start
from assvcPackage.clone import comExport, comImport

from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl, QDir

from assvcDestkopPackage.loading import run_with_loading


def new_repository(parent):
    dialog = QFileDialog(parent)
    dialog.setWindowTitle("Select Repository Folder")
    dialog.setFileMode(QFileDialog.Directory)
    dialog.setOption(QFileDialog.DontUseNativeDialog, False)

    if dialog.exec():
        folder_path = dialog.selectedFiles()[0]
        print("Selected folder:", folder_path)
        if start(folder_path):
            assvc_path = os.path.join(folder_path, '.assvc')
            open_new_window(parent, assvc_path)

def open_folder(parent, folder_path=None):
    if folder_path is None:
        dialog = QFileDialog(parent)
        dialog.setWindowTitle("Select Repository Folder (.assvc)")
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.DontUseNativeDialog, False)
        dialog.setFilter(QDir.AllDirs | QDir.Hidden)

        if dialog.exec():
            folder_path = dialog.selectedFiles()[0]
            
            if not folder_path.endswith('.assvc'):
                QMessageBox.warning(
                    parent,
                    "Invalid Selection",
                    "Please select a folder named '.assvc'"
                )
                return
            
            open_new_window(parent, folder_path)
    else:
        open_new_window(parent, folder_path)

def open_in_explorer(folder_path):
    QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))

def open_in_explorer_file(file_path):
    folder_path = os.path.dirname(file_path)
    QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))

def import_repository(parent):
    file_path, _ = QFileDialog.getOpenFileName(
        parent,
        "Select ZIP file to import",
        "",
        "ZIP archives (*.zip)"
    )

    if not file_path:
        return

    print("Selected zip:", file_path)

    dialog = QFileDialog(parent)
    dialog.setWindowTitle("Select destination folder for repository")
    dialog.setFileMode(QFileDialog.Directory)
    dialog.setOption(QFileDialog.DontUseNativeDialog, False)

    if dialog.exec():
        dest_folder = dialog.selectedFiles()[0]
        print("Destination folder:", dest_folder)
        
        def do_import():
            original_dir = os.getcwd()
            try:
                os.chdir(dest_folder)
                comImport(file_path)
            finally:
                os.chdir(original_dir)
        
        try:
            run_with_loading(
                parent, 
                do_import,
                title="Importing",
                message="Importing repository...\nPlease wait."
            )

        except Exception as e:
            QMessageBox.critical(parent, "Import Failed", f"Failed to import repository:\n{str(e)}")

def export_repository(folder_path, parent=None):
    dialog = QFileDialog()
    dialog.setWindowTitle("Select destination folder for exported ZIP")
    dialog.setFileMode(QFileDialog.Directory)
    dialog.setOption(QFileDialog.DontUseNativeDialog, False)

    if dialog.exec():
        save_folder = dialog.selectedFiles()[0]
        print("Exporting to folder:", save_folder)
        
        try:
            run_with_loading(
                parent,
                comExport,
                save_path=save_folder,
                repo_path=folder_path,
                title="Exporting",
                message="Exporting repository...\nPlease wait."
            )
            QMessageBox.information(parent, "Export Complete", "Repository exported successfully!")
        except Exception as e:
            QMessageBox.critical(parent, "Export Failed", f"Failed to export repository:\n{str(e)}")

def open_new_window(parent, message=None):
    from assvcDestkopPackage.child_window import ChildWindow

    child = ChildWindow(message)
    
    if not hasattr(parent, 'child_windows'):
        parent.child_windows = []
    parent.child_windows.append(child)
    
    child.show()
    parent.hide()

def return_to_main(parent):
    from assvcDestkopPackage.main_window import MainWindow
    
    app = QApplication.instance()
    main_window = None
    
    for widget in app.topLevelWidgets():
        if isinstance(widget, MainWindow) and widget != parent:
            main_window = widget
            break
    
    if isinstance(parent, MainWindow):
        parent.show()
        return
    
    if hasattr(parent, 'child_windows'):
        for child in parent.child_windows:
            if child and not child.isHidden():
                child.close()
    
    if main_window:
        main_window.show()
        parent.close()
    else:
        main_window = MainWindow()
        main_window.show()
        parent.close()