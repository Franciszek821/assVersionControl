import os
import traceback

def is_debug_mode():
    """Check if DEBUG mode is enabled from .env file"""
    try:
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if line.strip().startswith('DEBUG='):
                        return line.split('=')[1].strip().lower() in ('true', '1', 'yes')
    except Exception:
        pass
    return False

def show_warning(parent=None, title="", message="", exception=None):
    debug = is_debug_mode()
    
    full_message = message
    if debug and exception:
        full_message += f"\n\n--- Debug Info ---\n{str(exception)}\n\nTraceback:\n{''.join(traceback.format_tb(exception.__traceback__))}"
    
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox
        if QApplication.instance() is not None:
            if debug:
                print(f"\n❌ {title}: {full_message}\n")
            QMessageBox.warning(
                parent,
                title,
                full_message,
                QMessageBox.Ok
            )
        else:
            print(f"\n❌ {title}: {full_message}\n")
    except ImportError:
        print(f"\n❌ {title}: {full_message}\n")