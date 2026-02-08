import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from warning import show_warning

from assvcPackage.compare import compare
from assvcPackage.utils import find_assvc, get_ignore

def stage(file_paths=None, stage_all=False):
    if stage_all:
        return stageAll()
    assvc_path = find_assvc()
    if assvc_path is None:
        show_warning(None, "Repository Error", "directory does not contain an assvc repository (run `assvc start` first).")
        return
    
    if file_paths is None or len(file_paths) == 0:
        show_warning(None, "Stage Error", "No file paths provided to stage.")
        return

    if isinstance(file_paths, (str, os.PathLike)):
        file_paths = [file_paths]

    result = compare("latest", False, True, True)
    if result and isinstance(result, tuple):
        changes = result[0]
    else:
        changes = result or []
    
    changed_set = {os.path.abspath(p[0]) if isinstance(p, tuple) else os.path.abspath(p) for p in changes}

    index_path = os.path.join(assvc_path, "index")
    already_staged = set()
    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            already_staged = {line.strip() for line in f if line.strip()}

    for fp in file_paths:
        abs_fp = os.path.abspath(fp)
        if abs_fp in changed_set:
            if abs_fp in already_staged:
                print(f"Info: '{abs_fp}' is already staged.")
                continue
            with open(index_path, "a") as f:
                f.write(abs_fp + "\n")
            print(f"Staged: {abs_fp}")
        else:
            if not os.path.exists(abs_fp):
                show_warning(None, "File Error", f"'{abs_fp}' does not exist in the working directory or commit history.")
            else:
                show_warning(None, "Stage Error", f"The file '{abs_fp}' does not have any changes to stage.")

def unstage(file_paths):
    
    assvc_path = find_assvc()
    if assvc_path is None:
        show_warning(None, "Repository Error", "not an assvc repository (run `assvc start` first).")
        return

    if isinstance(file_paths, (str, os.PathLike)):
        file_paths = [file_paths]

    index_path = os.path.join(assvc_path, "index")
    if not os.path.exists(index_path):
        show_warning(None, "Stage Error", "No files are currently staged.")
        return

    with open(index_path, "r") as f:
        staged_files = {line.strip() for line in f if line.strip()}

    with open(index_path, "w") as f:
        for sf in staged_files:
            sf = os.path.abspath(sf)
            file_paths = [os.path.abspath(fp) for fp in file_paths]
            if sf not in file_paths:
                f.write(sf + "\n")
            else:
                print(f"Unstaged: {sf}")

def clear():
    assvc_path = find_assvc()
    if assvc_path is None:
        show_warning(None, "Repository Error", "not an assvc repository (run `assvc start` first).")
        return

    index_path = os.path.join(assvc_path, "index")
    if os.path.exists(index_path):
        os.remove(index_path)
        print("Cleared all staged files.")
    else:
        print("No files are currently staged.")


def seeStaged(isPrint=True):
    listStaged = []
    assvc_path = find_assvc()
    if assvc_path is None:
        show_warning(None, "Repository Error", "not an assvc repository (run `assvc start` first).")
        return

    index_path = os.path.join(assvc_path, "index")
    if not os.path.exists(index_path):
        if isPrint:
            print("No files are currently staged.")
        return

    with open(index_path, "r") as f:
        staged_files = [line.strip() for line in f if line.strip()]

    if not staged_files:
        print("No files are currently staged.")
    else:
        if isPrint:
            print("Staged files:")
        for sf in staged_files:
            listStaged.append(sf)
            if isPrint:
                print(f" - {sf}")
        return listStaged

def stageAll():
    assvc_path = find_assvc()
    if assvc_path is None:
        show_warning(None, "Repository Error", "not an assvc repository (run `assvc start` first).")
        return

    result = compare("latest", False, True, True)
    if result and isinstance(result, tuple):
        changes = result[0]
    else:
        changes = result or []
    
    if not changes:
        print("No changes to stage.")
        return

    index_path = os.path.join(assvc_path, "index")
    with open(index_path, "w") as f:
        for change in changes:
            path = change[0] if isinstance(change, tuple) else change
            f.write(os.path.abspath(path) + "\n")
    print(f"Staged all changes ({len(changes)} files).")

def unstageAll():
    assvc_path = find_assvc()
    if assvc_path is None:
        show_warning(None, "Repository Error", "not an assvc repository (run `assvc start` first).")
        return

    index_path = os.path.join(assvc_path, "index")
    if os.path.exists(index_path):
        os.remove(index_path)
        print("Unstaged all files.")
    else:
        print("No files are currently staged.")

def isStaged(path):
    assvc_path = find_assvc()
    if assvc_path is None:
        return False
    
    index_path = os.path.join(assvc_path, "index")
    if not os.path.exists(index_path):
        return False
    
    abs_path = os.path.abspath(path)
    
    try:
        with open(index_path, "r") as f:
            staged_files = {line.strip() for line in f if line.strip()}
        return abs_path in staged_files
    except Exception:
        return False