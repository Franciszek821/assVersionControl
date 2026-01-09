import os
import hashlib
import zlib
import time
import difflib

from assvcPackage.commit import find_assvc
from assvcPackage.commit import ignore_dirs


assvc_path = find_assvc()
if assvc_path:
    parent_path = os.path.dirname(assvc_path)


def compare():
    if not assvc_path:
        print("Error: .assvc directory not found.Chuj")
        return
    
    current_path = os.path.join(assvc_path, "head/current")
    with open(current_path, "r") as f:
        commit_sha = f.read().strip()

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
            #print(f"FILE: {path}")
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
            dirsFilesAll.append(os.path.join(root, d))
        for f in files:
            dirsFilesAll.append(os.path.join(root, f))


    for (path, sha) in path_check:

        if not os.path.exists(path):
            print(f"{RED}  MISSING:{RESET} {path}")
            continue

        if not is_text_file(path):
            continue

        size = os.path.getsize(path)
        with open(path, "r", encoding="utf-8") as f:
            fileContent = f.read()

        shapath = os.path.join(assvc_path, "objects", sha[:2], sha)
        with open(shapath, "rb") as f:
            compressed = f.read()
        old_content = zlib.decompress(compressed).decode("utf-8", errors="replace")

        now_blob = "blob" + str(size) + "\n" + fileContent
        shaNow = hashlib.sha1(now_blob.encode()).hexdigest()

        if shaNow != sha:
            print(f"{YELLOW}  MODIFIED:{RESET} {path}")
            old_content_lines = "\n".join(old_content.split("\n")[1:])
            now_blob_lines = "\n".join(now_blob.split("\n")[1:])
            show_diff(old_content_lines, now_blob_lines, path)


    tracked_paths = [path for path, sha in path_check]
    for item in dirsFilesAll:
        if item not in tracked_paths:
            print(f"{GREEN}  NEW:{RESET} {item}")
    






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
        text = decompressed.decode("utf-8")
    except UnicodeDecodeError:
        text = decompressed 
    return text

def is_text_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            f.read()
        return True
    except (UnicodeDecodeError, OSError):
        return False


def show_diff(old_text, new_text, filename):
    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)

    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=filename + " (previous)",
        tofile=filename + " (current)",
        lineterm=""
    )

    for line in diff:
        if line.startswith("+") and not line.startswith("+++"):
            print("\033[32m" + line + "\033[0m")  # green
        elif line.startswith("-") and not line.startswith("---"):
            print("\033[31m" + line + "\033[0m")  # red




#compare()