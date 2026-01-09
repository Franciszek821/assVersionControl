import os
import sys
import shutil
import stat


def setup():
    config_path = os.path.expanduser("~/.config/assvc/config")
    os.makedirs(config_path, exist_ok=True)

    commiter = input("Enter the username to setup: ")

    file_path = os.path.join(config_path, "commiter")
    if os.path.exists(file_path):
        os.remove(file_path)
    with open(config_path + "/commiter", "w") as f:
        f.write(commiter)
    print(f"Username set to: {commiter}")

