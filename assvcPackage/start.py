import os
import getpass



def start():
    try:
        if os.path.exists(".assvc"):
            print("Error: .assvc directory already exists in the current folder")
            return
        
        commiter = getpass.getuser()
        print(f"Current commiter: {commiter}")
        
        os.makedirs('.assvc', exist_ok=True)
        print("Created .assvc directory")
        
        os.makedirs('.assvc/objects', exist_ok=True)
        print("Created .assvc/objects directory")
        
        os.makedirs('.assvc/history', exist_ok=True)
        print("Created .assvc/history directory")
        
        os.makedirs('.assvc/head', exist_ok=True)
        print("Created .assvc/head directory")
        
        # Create empty history file
        history_file = os.path.join('.assvc', 'history', 'history')
        with open(history_file, 'w') as f:
            pass
        print("Created history file")
        
        print("\n✓ Repository initialized successfully!")
        print("Use 'assvc staging stage -a' to stage files")
        print("Use 'assvc commit -m \"message\"' to create your first commit")
        
    except PermissionError:
        print("Error: Permission denied. Unable to create directories in the current location.")
    except OSError as e:
        print(f"Error: Unable to initialize repository. {str(e)}")
    except Exception as e:
        print("Error: An unexpected error occurred during initialization.")



