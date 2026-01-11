#!/usr/bin/env python3

import os
import shutil
import stat
import sys

SRC_NAME = "assvcLinux"
TARGET_DIR = os.path.expanduser("~/.local/bin")
TARGET_PATH = os.path.join(TARGET_DIR, "assvc")

def install():
    if os.path.exists(TARGET_PATH):
        input("assvc is already installed. Press Enter to remove it...")
        os.remove(TARGET_PATH)
        print("assvc removed")
        return

    input("Press Enter to install assvc...")

    if not os.path.isfile(SRC_NAME):
        print(f"Error: '{SRC_NAME}' not found in current directory")
        sys.exit(1)

    os.makedirs(TARGET_DIR, exist_ok=True)

    # Ensure executable bit before install
    st = os.stat(SRC_NAME)
    os.chmod(
        SRC_NAME,
        st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    )

    # Move AND rename
    shutil.move(SRC_NAME, TARGET_PATH)

    print(f"Installed assvc to {TARGET_DIR}")
    setup()

def setup():
    config_path = os.path.expanduser("~/.config/assvc/config")
    os.makedirs(config_path, exist_ok=True)

    username = input("Enter username name: ")

    with open(config_path + "/username", "w") as f:
        f.write(username)