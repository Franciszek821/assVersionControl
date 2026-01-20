import os
import hashlib
import zlib
import time
import difflib

from assvcPackage.utils import (find_assvc, get_ignore, deShorten_sha, get_history, extractDataCommit, extractDataTree, extractData,
                                 show_diff, is_text_bytes, extractCommitText)

comparePrintGlobal = None
changesMade = []

def compare(commit_sha, show_diff_var, comparePrint, noPrint=False):
    global comparePrintGlobal
    global changesMade
    
    assvc_path = find_assvc()
    if not assvc_path:
        print("Error: .assvc directory not found.")
        return
    
    parent_path = os.path.dirname(assvc_path)
    ignore_dirs, ignore_files = get_ignore(parent_path)
    try:
        comparePrintGlobal = comparePrint
        if commit_sha == "latest":
            current_path = os.path.join(find_assvc(), "head/current")
            try:
                with open(current_path, "r") as f:
                    commit_sha = f.read().strip()
            except IOError:
                if not noPrint:
                    print("Info: No commits yet. All files will be considered new.")
                all_files = []
                for root, dirs, files in os.walk(parent_path):
                    dirs[:] = [d for d in dirs if d not in ignore_dirs]
                    for f in files:
                        if f not in ignore_files:
                            all_files.append(os.path.join(root, f))
                return all_files

        commit_text = extractCommitText(commit_sha)
        if commit_text is None:
            return

        treeSHA, commiter, timestamp, message = extractDataCommit(commit_text)

        if not noPrint:
            if comparePrintGlobal:
                print(f"Comparing with commit: {commiter} {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(timestamp)))}")
                print(f"Message: {message}")
            else:
                print(f"Reversing with commit: {commiter} {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(timestamp)))}")
                print(f"Message: {message}")
                print("\n")
                print("THE REVERT WILL")

        root_tree_path = os.path.join(assvc_path, "objects", treeSHA[:2], treeSHA)
        try:
            with open(root_tree_path, "rb") as f:
                tree_data = zlib.decompress(f.read())
        except Exception:
            print("Error: Could not read tree data.")
            return
        stack = extractDataTree(tree_data.decode())
        path_check = []
        while stack:
            entry_type, name, sha = stack.pop()
            try:
                object_data = extractData(sha)
            except Exception:
                print(f"Warning: Could not read object {sha}")
                continue
            if isinstance(object_data, str):
                object_data = object_data.encode()
            if entry_type == "16384":
                if name:
                    dir_path = os.path.join(parent_path, name)
                    path_check.append((dir_path, sha))
                try:
                    children = extractDataTree(object_data.decode())
                except Exception:
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

        check(path_check, show_diff_var, noPrint, parent_path, ignore_dirs, ignore_files, assvc_path)
        return changesMade
    except Exception:
        print("Error: An unexpected error occurred during comparison.")

# colors
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
RESET  = "\033[0m"

def check(path_check, show_diff_var, noPrint, parent_path, ignore_dirs, ignore_files, assvc_path):
    global comparePrintGlobal
    global changesMade
    try:
        
        if not noPrint:
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
            if not os.path.exists(path) or not os.path.isfile(path):
                continue
            
            try:
                with open(path, "rb") as f:
                    file_content = f.read()
        
                shapath = os.path.join(assvc_path, "objects", sha[:2], sha)
                with open(shapath, "rb") as f:
                    compressed = f.read()
        
                old_blob_full = zlib.decompress(compressed)
                header_end = old_blob_full.find(b'\n')
                old_content = old_blob_full[header_end+1:]
        
                now_blob_full = b"blob " + str(len(file_content)).encode() + b"\n" + file_content
                shaNow = hashlib.sha1(now_blob_full).hexdigest()
        
                if shaNow != sha:
                    if comparePrintGlobal:
                        if not noPrint:
                            print(f"{YELLOW}  MODIFIED:{RESET} {path}")
                        changesMade.append(path)
                    else:
                        print(f"{YELLOW}  MODIFY:{RESET} {path}")
        
                    if show_diff_var:
                        if is_text_bytes(old_content):
                            old_text = old_content.decode('utf-8', errors='replace')
                            new_text = file_content.decode('utf-8', errors='replace')
                            show_diff(old_text, new_text, path)
                        else:
                            if not noPrint:
                                print(f"{YELLOW}  MODIFIED (binary, no diff):{RESET} {path}")
            except Exception:
                print(f"Warning: Could not process file {path}")
        tracked_paths = [path for path, sha in path_check]
        for item in dirsFilesAll:
            if item not in tracked_paths:
                if comparePrintGlobal:
                    if not noPrint:
                        print(f"{GREEN}  NEW:{RESET} {item}")
                    changesMade.append(item)
                else:
                    print(f"{RED}  DELETE:{RESET} {item}")

        commit_paths = [path for path, sha in path_check]
        
        for path in commit_paths:
            if not os.path.exists(path):
                if comparePrintGlobal:
                    if not noPrint:
                        print(f"{RED}  DELETED:{RESET} {path}")
                    changesMade.append(path)
                else:
                    print(f"{GREEN}  ADD:{RESET} {path}")
        
    except Exception:
        print("Error: An error occurred during comparison check.")




# test
