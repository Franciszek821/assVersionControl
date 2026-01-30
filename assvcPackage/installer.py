#!/usr/bin/env python3

import os
import shutil
import stat
import sys
import platform

def get_install_paths():
    system = platform.system()
    
    if system == "Windows":
        src_name = "assvcWindows.exe"
        target_dir = os.path.join(os.environ.get("LOCALAPPDATA", ""), "assvc")
        target_path = os.path.join(target_dir, "assvc.exe")
    else:
        src_name = "assvcLinux"
        target_dir = os.path.expanduser("~/.local/bin")
        target_path = os.path.join(target_dir, "assvc")
    
    return src_name, target_dir, target_path

def install():
    try:
        SRC_NAME, TARGET_DIR, TARGET_PATH = get_install_paths()
        
        if os.path.exists(TARGET_PATH):
            try:
                input("assvc is already installed. Press Enter to remove it...")
            except KeyboardInterrupt:
                print("\nInstallation cancelled.")
                return
            try:
                os.remove(TARGET_PATH)
                print("assvc removed")
            except PermissionError:
                print("Error: Permission denied when removing existing installation.")
                return
            except OSError:
                print("Error: Could not remove existing installation.")
                return
            return

        try:
            input("Press Enter to install assvc...")
        except KeyboardInterrupt:
            print("\nInstallation cancelled.")
            return

        if not os.path.isfile(SRC_NAME):
            print(f"Error: '{SRC_NAME}' not found in current directory")
            sys.exit(1)

        try:
            os.makedirs(TARGET_DIR, exist_ok=True)
        except PermissionError:
            print("Error: Permission denied. Could not create target directory.")
            sys.exit(1)
        except OSError:
            print("Error: Could not create target directory.")
            sys.exit(1)

        if platform.system() != "Windows":
            try:
                st = os.stat(SRC_NAME)
                os.chmod(
                    SRC_NAME,
                    st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
                )
            except OSError:
                print("Error: Could not set executable permissions.")
                sys.exit(1)

        try:
            shutil.move(SRC_NAME, TARGET_PATH)
        except PermissionError:
            print("Error: Permission denied. Could not move assvc to target location.")
            sys.exit(1)
        except shutil.Error:
            print("Error: Could not move assvc to target location.")
            sys.exit(1)

        print(f"Installed assvc to {TARGET_DIR}")
        
        if platform.system() == "Windows":
            print(f"Add {TARGET_DIR} to your PATH environment variable to use assvc globally.")
        
    except Exception:
        print("Error: An unexpected error occurred during installation.")
        sys.exit(1)

