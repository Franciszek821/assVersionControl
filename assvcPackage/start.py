import os
import getpass
from assvcPackage.commit import commit



def start():
    if os.path.exists(".assvc"):
        print("Error: .assvc directory already exists in the current folder")
        return
    commiter = user = getpass.getuser()
    print(f"Current commiter: {commiter}")
    os.makedirs('.assvc', exist_ok=True)
    print("Created .assvc directory")
    os.makedirs('.assvc/objects', exist_ok=True)
    print("Created .assvc/objects directory")
    os.makedirs('.assvc/history', exist_ok=True)
    print("Created .assvc/history directory")
    os.makedirs('.assvc/objects', exist_ok=True)
    print("Created .assvc/objects directory")
    commit(message="Initial commit")



