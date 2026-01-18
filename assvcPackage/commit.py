import getpass
import os
import hashlib
import zlib
import time
import platform


def depth(parent):
    return 0 if parent == "" else parent.count(os.sep) + 1

def commit(message):
    try:
        assvc_path = find_assvc()
        if assvc_path is None:
            print("Error: not an assvc repository (run `assvc start` first)")
            return

        parent_path = os.path.dirname(assvc_path)
        
        ignore_dirs, ignore_files = get_ignore(parent_path)
        blobs_by_parent = {}
        dir_by_parent = {}
        item_by_parent = {}
        tree_sha = {}

        for root, dirs, files in os.walk(parent_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
            rel_root = os.path.relpath(root, parent_path)
            if rel_root == '.':
                rel_root = ""
            
            blob_list = []
            for file in files:
                if file in ignore_files:
                    continue
                file_path = os.path.join(root, file)
                if not is_text_file(file_path):
                    continue
                try:
                    shaName, mode = make_blob(file_path, assvc_path)
                    blob_entry = f"{mode} {file} {shaName}"
                    blob_list.append(blob_entry)
                except Exception as e:
                    print(f"Warning: Skipping file {file_path} - unable to process")
                    continue

            blobs_by_parent[rel_root] = blob_list
        
            dir_list = []
            for d in dirs:
                if d in ignore_dirs:
                    continue
                dir_path = os.path.join(root, d)
                dir_list.append(d)
        
                if os.path.isdir(dir_path) and not os.listdir(dir_path):
                    try:
                        make_tree_empty_dir(os.path.relpath(dir_path, parent_path), assvc_path, tree_sha)
                    except Exception:
                        pass
        
            dir_by_parent[rel_root] = dir_list

        for parent in blobs_by_parent.keys():
            item_by_parent[parent] = {
                "blobs": blobs_by_parent.get(parent, []),
                "directory": dir_by_parent.get(parent, [])
            }

        for parent in sorted(item_by_parent.keys(),
                             key=lambda p: 0 if p == "" else len(p.split(os.sep)),
                             reverse=True):
            blobs = item_by_parent[parent]["blobs"]
            directory = item_by_parent[parent]["directory"]
            tree_root_sha = make_tree(parent, blobs, directory, assvc_path, tree_sha)
            
        make_commit(tree_root_sha, assvc_path, message)
    except PermissionError:
        print("Error: Permission denied. Unable to access files for commit.")
    except Exception as e:
        print("Error: An unexpected error occurred during commit.")

def make_blob(file_path, assvc_path):
    try:
        size = os.path.getsize(file_path)

        with open(file_path, "r", encoding="utf-8") as f:
            fileContent = f.read()

        blobContent = "blob " + str(size) + "\n" + fileContent
        sha = hashlib.sha1(blobContent.encode()).hexdigest()
        compressed = zlib.compress(blobContent.encode())
        first_two = sha[:2]
        objects_dir = os.path.join(assvc_path, "objects", first_two)
        os.makedirs(objects_dir, exist_ok=True)
        blob_path = os.path.join(objects_dir, sha)
        with open(blob_path, "wb") as f:
            f.write(compressed)
        
        import platform
        if platform.system() == "Windows":
            mode = 0o100644  # Default file mode
        else:
            st = os.stat(blob_path)
            mode = st.st_mode & 0o777
        return sha, mode
    except IOError:
        raise Exception(f"Cannot read file: {file_path}")
    except Exception as e:
        raise

def make_tree(parent, blob, directory, assvc_path, tree_sha):
    try:
        mode = 0o40000
        parentContent = []
        for b in blob:
            b_content = f"{b}\n"
            parentContent.append(b_content)
        for d in directory:
            child_key = os.path.join(parent, d) if parent else d
            child_shas = tree_sha.get(child_key)
            child_ref = child_shas[-1] if child_shas else ""
            d_content = f"{mode} {d} {child_ref}\n"
            parentContent.append(d_content)
        
        sha = hashlib.sha1("".join(parentContent).encode()).hexdigest()
        compressed = zlib.compress("".join(parentContent).encode())
        first_two = sha[:2]
        objects_dir = os.path.join(assvc_path, "objects", first_two)
        os.makedirs(objects_dir, exist_ok=True)
        parent_path = os.path.join(objects_dir, sha)
        with open(parent_path, "wb") as f:
            f.write(compressed)

        if parent == "":
            return sha
            
        tree_sha.setdefault(parent, []).append(sha)
    except Exception:
        raise Exception("Error creating tree object")

def make_tree_empty_dir(dir, assvc_path, tree_sha):
    try:
        mode = 0o40000
        tree_content = b""
        dirContent = b"tree " + str(len(tree_content)).encode() + b"\0" + tree_content
        
        sha = hashlib.sha1(dirContent).hexdigest()
        compressed = zlib.compress(dirContent)
        first_two = sha[:2]
        objects_dir = os.path.join(assvc_path, "objects", first_two)
        os.makedirs(objects_dir, exist_ok=True)
        parent_path = os.path.join(objects_dir, sha)
        with open(parent_path, "wb") as f:
            f.write(compressed)

        tree_sha.setdefault(dir, []).append(sha)
        return sha
    except Exception:
        raise Exception("Error creating empty directory tree")

def make_commit(tree_root_sha, assvc_path, message):
    try:
        os.makedirs(os.path.join(assvc_path, 'head'), exist_ok=True)

        commiter = getpass.getuser()
        timestamp = int(time.time())
        commit_content = f"tree {tree_root_sha}\ncommiter {commiter} {timestamp}\n\n{message}\n"
        sha = hashlib.sha1(commit_content.encode()).hexdigest()
        compressed = zlib.compress(commit_content.encode())
        first_two = sha[:2]
        objects_dir = os.path.join(assvc_path, "objects", first_two)
        os.makedirs(objects_dir, exist_ok=True)
        commit_path = os.path.join(objects_dir, sha)
        with open(commit_path, "wb") as f:
            f.write(compressed)
        print(f"Commit created Message: {message} SHA: {shorten_sha(sha, get_history(assvc_path))}")
        current_file = os.path.join(assvc_path, 'head', 'current')
        with open(current_file, "w") as f:
            f.write(sha)
        save_history(assvc_path, sha)
        return sha
    except PermissionError:
        print("Error: Permission denied while creating commit.")
    except Exception:
        print("Error: Failed to create commit.")

def is_text_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            f.read()
        return True
    except (UnicodeDecodeError, OSError):
        return False

def find_assvc():
    try:
        assvc_path = os.path.join(os.getcwd(), ".assvc")
        return assvc_path if os.path.exists(assvc_path) else None
    except Exception:
        return None

def save_history(assvc_path, sha):
    try:
        with open(get_history(assvc_path), "a") as f:
            f.write(sha + '\n')
    except IOError:
        print("Warning: Could not save history")

def get_ignore(parent_path):
    ignore_files = set()
    ignore_dirs = {'.assvc', '.git', '__pycache__'}

    assignore_path = os.path.join(parent_path, ".assignore")
    try:
        if not os.path.isfile(assignore_path):
            return ignore_dirs, ignore_files

        with open(assignore_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                if line.startswith("/"):
                    ignore_dirs.add(line.lstrip("/"))
                else:
                    ignore_files.add(line)
    except IOError:
        print("Warning: Could not read .assignore file")

    return ignore_dirs, ignore_files



def get_history(assvc_path):
    history_path = os.path.join(assvc_path, "history", "history")
    return history_path


def shorten_sha(full_sha, history_path):
    try:
        with open(history_path, "r") as f:
            commits = f.readlines()
    except IOError:
        print("Error: Unable to read history file.")
        return
    for i in range(7, len(full_sha) + 1):
        shorten_sha = full_sha[:i]
        for commit_sha in commits:
            if commit_sha.strip().startswith(shorten_sha):
                return shorten_sha
            else:
                continue
    return full_sha

def deShorten_sha(short_sha, history_path):
    try:
        with open(history_path, "r") as f:
            commits = f.readlines()
    except IOError:
        print("Error: Unable to read history file.")
        return
    for i in commits:
        if i.strip().startswith(short_sha):
            return i.strip()
    print("Error: No commit found with the given short SHA.")
    return None

