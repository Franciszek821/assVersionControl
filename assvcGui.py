import sys
import os
from PySide6.QtWidgets import QApplication
from assvcDestkopPackage.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    main_window = MainWindow()
    main_window.show()
    
    sys.exit(app.exec())
