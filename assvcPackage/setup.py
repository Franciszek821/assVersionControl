import os

def setup():
    config_path = os.path.expanduser("~/.config/assvc/config")
    os.makedirs(config_path, exist_ok=True)     # <-- FIX

    commiter = input("Enter commiter name: ")

    with open(config_path + "/commiter", "w") as f:
        f.write(commiter)
