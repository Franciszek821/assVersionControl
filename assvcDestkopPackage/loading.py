import os
import sys

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QMovie


class WorkerThread(QThread):

    finished = Signal(object)
    error = Signal(Exception)
    
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.result = None
    
    def run(self):
        try:
            self.result = self.func(*self.args, **self.kwargs)
            self.finished.emit(self.result)
        except Exception as e:
            self.error.emit(e)


class LoadingDialog(QDialog):

    
    def __init__(self, parent=None, title="Processing", message="Please wait..."):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(300, 120)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        
        layout = QVBoxLayout(self)
        

        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 14px; padding: 10px;")
        layout.addWidget(self.label)
        

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)
        layout.addWidget(self.progress)
        
        self.worker = None
    
    def run_task(self, func, *args, **kwargs):
        self.worker = WorkerThread(func, *args, **kwargs)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()
        self.exec()
        return getattr(self, '_task_result', None)
    
    def _on_finished(self, result):
        self._task_result = result
        self._task_error = None
        self.accept()
    
    def _on_error(self, error):
        self._task_result = None
        self._task_error = error
        self.reject()
    
    def get_error(self):
        return getattr(self, '_task_error', None)


def run_with_loading(parent, func, *args, title="Processing", message="Please wait...", **kwargs):
    dialog = LoadingDialog(parent, title, message)
    result = dialog.run_task(func, *args, **kwargs)
    
    error = dialog.get_error()
    if error:
        raise error
    
    return result
