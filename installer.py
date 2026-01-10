#!/usr/bin/env python3

import os
import shutil
import stat
import sys

BIN_NAME = "assvc"
TARGET_DIR = os.path.expanduser("~/.local/bin")
TARGET_PATH = os.path.join(TARGET_DIR, BIN_NAME)
path = os.path.expanduser("~/.local/bin/assvc")

def main():
    if os.path.exists(path):
        input("Assvc installed, do you want to remove it? Press Enter to confirm...")
        os.remove(path)
        print("assvc removed")
        return
    else:
        input("Do you want to install assvc? Press Enter to confirm...")
        if not os.path.isfile(BIN_NAME):
            print(f"Error: '{BIN_NAME}' not found in current directory")
            sys.exit(1)

        os.makedirs(TARGET_DIR, exist_ok=True)
        st = os.stat(BIN_NAME)
        os.chmod(BIN_NAME, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        shutil.copy2(BIN_NAME, TARGET_PATH)

        print(f"Installed '{BIN_NAME}' to {TARGET_DIR}")
        print("Restart your shell if the command is not found immediately.")

if __name__ == "__main__":
    main()
