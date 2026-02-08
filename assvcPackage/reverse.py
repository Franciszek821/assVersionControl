import os
import hashlib
import zlib
import time
import difflib
import shutil
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from warning import show_warning

from assvcPackage.utils import (find_assvc, get_ignore, deShorten_sha, get_history,
                                 extractDataCommit, extractDataTree, extractData)
from assvcPackage.compare import compare

def reverse(commit_sha = "latest", isPrintArgument=False, isForce=False, file_path=None):
    try:
        isPrint = isPrintArgument
        assvc_path = find_assvc()
        if not assvc_path:
            show_warning(None, "Repository Error", ".assvc directory not found.")
            return
        parent_path = os.path.dirname(assvc_path)
        ignore_dirs, ignore_files = get_ignore(parent_path)
        
        try:
            if commit_sha == "latest":
                current_path = os.path.join(find_assvc(), "head/current")
                with open(current_path, "r") as f:
                    commit_sha = f.read().strip()
            commit_sha = deShorten_sha(commit_sha, get_history(assvc_path))


            if isPrint and not file_path:
                compare(commit_sha=commit_sha, show_diff_var=False, comparePrint=False)
                print("\n")
                if not isForce:
                    confirmation = input(
                        f"are you sure you want to reverse to commit {commit_sha}? (y/n): "
                    )

                    if confirmation.lower() != 'y':
                        print("Reverse operation cancelled.")
                        return

        except KeyboardInterrupt:
            print("\nReverse operation cancelled.")
            return
        except IOError as e:
            show_warning(None, "Read Error", "Could not read commit reference.", exception=e)
            return

        if not assvc_path:
            show_warning(None, "Repository Error", ".assvc directory not found.")
            return
        
        try:
            commit_path = os.path.join(assvc_path, "objects", commit_sha[:2], commit_sha)
            with open(commit_path, "rb") as f:
                compressed_data = f.read()
        except FileNotFoundError:
            show_warning(None, "Commit Error", f"Commit '{commit_sha}' not found.")
            return
        except IOError as e:
            show_warning(None, "Read Error", "Unable to read commit data.", exception=e)
            return

        try:
            decompressed = zlib.decompress(compressed_data)
            commit_text = decompressed.decode("utf-8", errors="replace")
        except Exception as e:
            show_warning(None, "Data Error", "Corrupted commit data.", exception=e)
            return

        treeSHA, commiter, timestamp, message = extractDataCommit(commit_text)
        if isPrint:
            print(f"Latest commit: {commiter} {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(timestamp)))}")
            print(f"Message: {message}")

        try:
            root_tree_path = os.path.join(assvc_path, "objects", treeSHA[:2], treeSHA)
            with open(root_tree_path, "rb") as f:
                tree_data = zlib.decompress(f.read())
        except Exception as e:
            show_warning(None, "Tree Error", "Could not read tree data.", exception=e)
            return

        if file_path:
            reverse_single_file(treeSHA, file_path, isPrint, assvc_path, parent_path)
            return

        stack = extractDataTree(tree_data.decode())
        path_check = []

        while stack:
            entry_type, name, sha = stack.pop()
            try:
                object_data = extractData(sha)
            except Exception as e:
                show_warning(None, "Object Warning", f"Could not read object {sha}", exception=e)
                continue

            if isinstance(object_data, str):
                object_data = object_data.encode()

            if entry_type == "16384":
                if name:
                    dir_path = os.path.join(parent_path, name)
                    path_check.append((dir_path, sha))

                try:
                    children = extractDataTree(object_data.decode())
                except Exception as e:
                    show_warning(None, "Tree Warning", f"Could not read tree data for {sha}", exception=e)
                    continue
                for (child_type, child_name, child_sha) in reversed(children):
                    full_name = os.path.join(name, child_name) if name else child_name
                    path = os.path.join(parent_path, full_name)
                    if child_type == "16384":
                        stack.append((child_type, full_name, child_sha))
                    else:
                        path_check.append((path, child_sha))
            else:
                path = os.path.join(parent_path, name)
                path_check.append((path, sha))
            
        check(path_check, isPrint, assvc_path, parent_path, ignore_dirs, ignore_files)
    except Exception as e:
        show_warning(None, "Reverse Error", "An unexpected error occurred during reverse operation.", exception=e)

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
RESET  = "\033[0m"

def check(path_check, isPrint=False, assvc_path=None, parent_path=None, ignore_dirs=None, ignore_files=None):
    try:
        if isPrint:
            print()

        dirsFilesAll = []
        for root, dirs, files in os.walk(parent_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for d in dirs:
                if d in ignore_dirs:
                    continue
                dirsFilesAll.append(os.path.join(root, d))
            for f in files:
                if f in ignore_files:
                    continue
                dirsFilesAll.append(os.path.join(root, f))

        for (path, sha) in path_check:
            if not os.path.exists(path):
                try:
                    restore_missing_file(path, sha)
                    if isPrint:
                        print(f"{GREEN}  REVERSED DELETE:{RESET} {path}")
                except Exception:
                    show_warning(None, "Restore Warning", f"Could not restore {path}")
                continue

            if not os.path.isfile(path):
                continue

            try:
                shapath = os.path.join(assvc_path, "objects", sha[:2], sha)
                with open(shapath, "rb") as f:
                    compressed = f.read()
                old_blob_full = zlib.decompress(compressed)
                header_end = old_blob_full.find(b'\n')
                old_content_bytes = old_blob_full[header_end+1:]

                with open(path, "rb") as f:
                    file_content = f.read()

                now_blob_full = b"blob " + str(len(file_content)).encode() + b"\n" + file_content
                shaNow = hashlib.sha1(now_blob_full).hexdigest()

                if shaNow != sha:
                    if isPrint:
                        print(f"{YELLOW}  REVERSED CHANGES:{RESET} {path}")
                    changeFileContent(path, old_content_bytes)
            except Exception:
                show_warning(None, "Reverse Warning", f"Could not reverse changes for {path}")
                continue

        tracked_paths = [path for path, sha in path_check]
        for item in dirsFilesAll:
            if item not in tracked_paths:
                try:
                    reverseAdd(item)
                    if isPrint:
                        print(f"{RED}  REVERSED NEW:{RESET} {item}")
                except Exception:
                    show_warning(None, "Remove Warning", f"Could not remove {item}")
    except Exception:
        show_warning(None, "Check Error", "An error occurred during reverse check.")

def changeFileContent(path, content_bytes):
    with open(path, "wb") as f:
        f.write(content_bytes)

def reverseAdd(item):
    if os.path.isfile(item):
        os.remove(item)
    elif os.path.isdir(item):
        shutil.rmtree(item)

def restore_missing_file(path, sha):
    current_assvc_path = find_assvc()
    if not current_assvc_path:
        raise Exception("Not an assvc repository")
    
    shapath = os.path.join(current_assvc_path, "objects", sha[:2], sha)
    with open(shapath, "rb") as f:
        compressed = f.read()
    data_full = zlib.decompress(compressed)
    
    if data_full.startswith(b'blob '):
        header_end = data_full.find(b'\n')
        content = data_full[header_end+1:]
        parent_dir = os.path.dirname(path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        with open(path, "wb") as f:
            f.write(content)
    else:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

def reverse_single_file(tree_sha, file_path, isPrint=False, assvc_path=None, parent_path=None):
    if not assvc_path:
        assvc_path = find_assvc()
    if not parent_path:
        parent_path = os.path.dirname(assvc_path)
    

    if os.path.isabs(file_path):
        rel_path = os.path.relpath(file_path, parent_path)
    else:
        rel_path = file_path
        file_path = os.path.join(parent_path, file_path)
    

    file_sha = find_file_in_tree(tree_sha, rel_path)
    
    if not file_sha:
        if os.path.exists(file_path):
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                if isPrint:
                    print(f"{RED}  REVERSED NEW:{RESET} {rel_path}")
            except Exception as e:
                show_warning(None, "Remove Error", f"Could not remove new file '{rel_path}': {e}")
        else:
            show_warning(None, "File Error", f"File '{rel_path}' not found in commit or working directory.")
        return
    

    try:
        shapath = os.path.join(assvc_path, "objects", file_sha[:2], file_sha)
        with open(shapath, "rb") as f:
            compressed = f.read()
        blob_full = zlib.decompress(compressed)
        header_end = blob_full.find(b'\n')
        content = blob_full[header_end+1:]
        

        parent_dir = os.path.dirname(file_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        if isPrint:
            print(f"{GREEN}  REVERSED:{RESET} {rel_path}")
    except Exception as e:
        show_warning(None, "Reverse Error", f"Could not reverse file '{rel_path}': {e}")

def find_file_in_tree(tree_sha, target_path):
    parts = target_path.split(os.sep)
    
    try:
        tree_data = extractData(tree_sha)
        if isinstance(tree_data, bytes):
            tree_data = tree_data.decode()
    except Exception:
        return None
    
    entries = extractDataTree(tree_data)
    

    if len(parts) == 1:
        for entry_type, name, sha in entries:
            if name == parts[0] and entry_type != "16384":
                return sha
        return None
    

    for entry_type, name, sha in entries:
        if entry_type == "16384" and name == parts[0]:
            remaining_path = os.sep.join(parts[1:])
            return find_file_in_tree(sha, remaining_path)
    
    return None




