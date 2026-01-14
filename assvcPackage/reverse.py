import os
import hashlib
import zlib
import time
import difflib
import shutil

from assvcPackage.commit import find_assvc
from assvcPackage.commit import get_ignore
from assvcPackage.compare import compare


assvc_path = find_assvc()
if assvc_path:
    parent_path = os.path.dirname(assvc_path)
    ignore_dirs, ignore_files = get_ignore(parent_path)


def reverse(commit_sha):
    try:
        if commit_sha == "latest":
            current_path = os.path.join(find_assvc(), "head/current")
            with open(current_path, "r") as f:
                commit_sha = f.read().strip()

        compare(commit_sha=commit_sha, show_diff_var=False, comparePrint=False)
        print("\n")

        confirmation = input(
            f"are you sure you want to reverse to commit {commit_sha}? (y/n): "
        )

        if confirmation.lower() != 'y':
            print("Reverse operation cancelled.")
            return

    except KeyboardInterrupt:
        print("\nReverse operation cancelled.")
        return

    

    if not assvc_path:
        print("Error: .assvc directory not found.")
        return
    

    commit_path = os.path.join(assvc_path, "objects", commit_sha[:2], commit_sha)
    with open(commit_path, "rb") as f:
        compressed_data = f.read()
    decompressed = zlib.decompress(compressed_data)
    commit_text = decompressed.decode("utf-8", errors="replace")

    treeSHA, commiter, timestamp, message = extractDataCommit(commit_text)
    print(f"Latest commit: {commiter} {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(timestamp)))}")
    print(f"Message: {message}")

    root_tree_path = os.path.join(assvc_path, "objects", treeSHA[:2], treeSHA)
    with open(root_tree_path, "rb") as f:
        tree_data = zlib.decompress(f.read())

    stack = extractDataTree(tree_data.decode())
    path_check = []

    while stack:
        entry_type, name, sha = stack.pop()
        object_data = extractData(sha)

        if isinstance(object_data, str):
            object_data = object_data.encode()

        if entry_type == "16384":
            if name:
                dir_path = os.path.join(parent_path, name)
                path_check.append((dir_path, sha))

            children = extractDataTree(object_data.decode())
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




# colors
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
RESET  = "\033[0m"


def check(path_check):
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
            restore_missing_file(path, sha)
            print(f"{GREEN}  REVERSED DELETE:{RESET} {path}")
            continue

        if not is_text_file(path):
            continue

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
            print(f"{YELLOW}  REVERSED CHANGES:{RESET} {path}")
            changeFileContent(path, commit_text)

    tracked_paths = [path for path, sha in path_check]
    for item in dirsFilesAll:
        if item not in tracked_paths:
            reverseAdd(item)
            print(f"{RED}  REVERSED NEW:{RESET} {item}")

def changeFileContent(path, commit_text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(commit_text)


def reverseAdd(item):
    if os.path.isfile(item):
        os.remove(item)
    elif os.path.isdir(item):
        shutil.rmtree(item)

def restore_missing_file(path, sha):
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



    


def extractDataCommit(commit_content):
    lines = commit_content.strip().splitlines()
    treeSHA = lines[0].split(" ", 1)[1]

    commiter_parts = lines[1].split(" ")
    commiter = commiter_parts[1]
    timestamp = commiter_parts[2]

    message = "\n".join(lines[3:])
    return treeSHA, commiter, timestamp, message


def extractDataTree(tree_content):
    lines = tree_content.strip().splitlines()
    entries = []
    for line in lines:
        parts = line.split(" ", 2)
        if len(parts) < 3:
            continue
        entry_type, name, sha = parts
        entries.append((entry_type, name, sha))
    return entries


def extractData(sha):
    path = assvc_path + "/objects/" + sha[:2] + "/" + sha
    with open(path, "rb") as f:
        compressed = f.read()
    decompressed = zlib.decompress(compressed)
    try:
        return decompressed.decode("utf-8")
    except UnicodeDecodeError:
        return decompressed


def is_text_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            f.read()
        return True
    except (UnicodeDecodeError, OSError):
        return False



