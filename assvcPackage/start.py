import os
import getpass
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from warning import show_warning



def start(path=os.getcwd()):
    try:
        if os.path.exists(os.path.join(path, ".assvc")):
            show_warning(None, "Repository Error", ".assvc directory already exists in the current folder")
            return False
        
        commiter = getpass.getuser()
        print(f"Current commiter: {commiter}")
        
        os.makedirs(os.path.join(path, '.assvc'), exist_ok=True)
        print("Created .assvc directory")
        
        os.makedirs(os.path.join(path, '.assvc', 'objects'), exist_ok=True)
        print("Created .assvc/objects directory")
        
        os.makedirs(os.path.join(path, '.assvc', 'history'), exist_ok=True)
        print("Created .assvc/history directory")
        
        os.makedirs(os.path.join(path, '.assvc', 'head'), exist_ok=True)
        print("Created .assvc/head directory")
        
        history_file = os.path.join(path, '.assvc', 'history', 'history')
        with open(history_file, 'w') as f:
            pass
        print("Created history file")
        
        print("\nRepository initialized successfully!")
        print("Use 'assvc staging stage -a' to stage files")
        print("Use 'assvc commit -m \"message\"' to create your first commit")
        return True
        
    except PermissionError:
        show_warning(None, "Permission Error", "Permission denied. Unable to create directories in the current location.")
        return False
    except OSError as e:
        show_warning(None, "OS Error", f"Unable to initialize repository. {str(e)}")
        return False
    except Exception as e:
        show_warning(None, "Initialization Error", "An unexpected error occurred during initialization.", exception=e)
        return False



