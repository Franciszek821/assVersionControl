import os
import hashlib
import zlib
import time
import difflib
import shutil

from assvcPackage.commit import find_assvc, get_ignore, get_history, deShorten_sha
from assvcPackage.compare import compare




global isPrint
global assvc_path
global parent_path
global ignore_dirs
global ignore_files
def reverse(commit_sha, isPrintArgument, isForce):
    global assvc_path, parent_path, ignore_dirs, ignore_files
    try:
        assvc_path = find_assvc()
        if assvc_path:
            parent_path = os.path.dirname(assvc_path)
            ignore_dirs, ignore_files = get_ignore(parent_path)
        global isPrint
        isPrint = isPrintArgument
        
        try:
            if commit_sha == "latest":
                current_path = os.path.join(find_assvc(), "head/current")
                with open(current_path, "r") as f:
                    commit_sha = f.read().strip()
            commit_sha = deShorten_sha(commit_sha, get_history(assvc_path))


            if isPrint:
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
        except IOError:
            print("Error: Could not read commit reference.")
            return

        if not assvc_path:
            print("Error: .assvc directory not found.")
            return
        
        try:
            commit_path = os.path.join(assvc_path, "objects", commit_sha[:2], commit_sha)
            with open(commit_path, "rb") as f:
                compressed_data = f.read()
        except FileNotFoundError:
            print(f"Error: Commit '{commit_sha}' not found.")
            return
        except IOError:
            print("Error: Unable to read commit data.")
            return

        try:
            decompressed = zlib.decompress(compressed_data)
            commit_text = decompressed.decode("utf-8", errors="replace")
        except Exception:
            print("Error: Corrupted commit data.")
            return

        treeSHA, commiter, timestamp, message = extractDataCommit(commit_text)
        if isPrint:
            print(f"Latest commit: {commiter} {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(timestamp)))}")
            print(f"Message: {message}")

        try:
            root_tree_path = os.path.join(assvc_path, "objects", treeSHA[:2], treeSHA)
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
            
        check(path_check)
    except Exception:
        print("Error: An unexpected error occurred during reverse operation.")

# colors
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
RESET  = "\033[0m"

def check(path_check):
    global isPrint
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
                    print(f"Warning: Could not restore {path}")
                continue

            if not is_text_file(path):
                continue

            try:
                size = os.path.getsize(path)
                with open(path, "r", encoding="utf-8") as f:
                    fileContent = f.read()

                shapath = os.path.join(assvc_path, "objects", sha[:2], sha)
                with open(shapath, "rb") as f:
                    compressed = f.read()

                old_blob_full = zlib.decompress(compressed).decode("utf-8", errors="replace")
                commit_text = old_blob_full.split("\n", 1)[1]

                now_blob_full = f"blob {size}\n{fileContent}"
                shaNow = hashlib.sha1(now_blob_full.encode()).hexdigest()

                if shaNow != sha:
                    if isPrint:
                        print(f"{YELLOW}  REVERSED CHANGES:{RESET} {path}")
                    changeFileContent(path, commit_text)
            except IOError:
                print(f"Warning: Could not process file {path}")
                continue
            except Exception:
                print(f"Warning: Could not reverse changes for {path}")
                continue

        tracked_paths = [path for path, sha in path_check]
        for item in dirsFilesAll:
            if item not in tracked_paths:
                try:
                    reverseAdd(item)
                    if isPrint:
                        print(f"{RED}  REVERSED NEW:{RESET} {item}")
                except Exception:
                    print(f"Warning: Could not remove {item}")
    except Exception:
        print("Error: An error occurred during reverse check.")

def changeFileContent(path, commit_text):
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(commit_text)
    except IOError:
        raise Exception(f"Cannot write to file: {path}")

def reverseAdd(item):
    try:
        if os.path.isfile(item):
            os.remove(item)
        elif os.path.isdir(item):
            shutil.rmtree(item)
    except PermissionError:
        raise Exception(f"Permission denied: {item}")
    except Exception as e:
        raise

def restore_missing_file(path, sha):
    try:
        parent_dir = os.path.dirname(path)

        if parent_dir and os.path.exists(parent_dir) and os.path.isfile(parent_dir):
            os.remove(parent_dir)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        shapath = os.path.join(assvc_path, "objects", sha[:2], sha)
        with open(shapath, "rb") as f:
            compressed = f.read()

        blob_full = zlib.decompress(compressed).decode("utf-8", errors="replace")
        content = blob_full.split("\n", 1)[1]

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    except IOError:
        raise Exception(f"Cannot restore file: {path}")
    except Exception as e:
        raise

def extractDataCommit(commit_content):
    try:
        lines = commit_content.strip().splitlines()
        treeSHA = lines[0].split(" ", 1)[1]

        commiter_parts = lines[1].split(" ")
        commiter = commiter_parts[1]
        timestamp = commiter_parts[2]

        message = "\n".join(lines[3:])
        return treeSHA, commiter, timestamp, message
    except (IndexError, ValueError):
        raise Exception("Corrupted commit data")

def extractDataTree(tree_content):
    try:
        lines = tree_content.strip().splitlines()
        entries = []
        for line in lines:
            parts = line.split(" ", 2)
            if len(parts) < 3:
                continue
            entry_type, name, sha = parts
            entries.append((entry_type, name, sha))
        return entries
    except Exception:
        return []

def extractData(sha):
    try:
        global assvc_path
        path = os.path.join(assvc_path, "objects", sha[:2], sha)
        with open(path, "rb") as f:
            compressed = f.read()
        decompressed = zlib.decompress(compressed)
        try:
            return decompressed.decode("utf-8")
        except UnicodeDecodeError:
            return decompressed
    except FileNotFoundError:
        raise Exception(f"Object {sha} not found")
    except Exception as e:
        raise

def is_text_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            f.read()
        return True
    except (UnicodeDecodeError, OSError):
        return False



