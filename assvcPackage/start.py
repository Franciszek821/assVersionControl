import os
from assvcPackage.commit import commit



def start():
    config_path = os.path.expanduser("~/.config/assvc/config/commiter")
    try:
        with open(config_path, "r") as f:
            commiter = f.read().strip()
            print(f"Current commiter: {commiter}")
    except FileNotFoundError:
        print("Commiter not set up. Please run the setup command first.")
    os.makedirs('.assvc', exist_ok=True)
    print("Created .assvc directory")
    os.makedirs('.assvc/objects', exist_ok=True)
    print("Created .assvc/objects directory")
    os.makedirs('.assvc/active', exist_ok=True)
    print("Created .assvc/active director")
    print("First commit with message \"initial commit\"")
    commit(message="initial commit")
