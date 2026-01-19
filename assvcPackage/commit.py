import getpass
import os
import hashlib
import zlib
import time
from assvcPackage.utils import find_assvc, get_ignore, get_history, shorten_sha, read_index, is_dir_empty, extractCommitText
from assvcPackage.stage import clear




def commit(message, stage_all=True):
    
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
        

        commitList = read_index(assvc_path)
        commitSet = {
            os.path.normpath(p)
            for p in commitList
        }
        

        previous_commit_files = {}
        current_path = os.path.join(assvc_path, "head/current")
        if os.path.exists(current_path):
            try:
                with open(current_path, "r") as f:
                    prev_commit_sha = f.read().strip()
                
                from assvcPackage.utils import extractDataCommit, extractDataTree, extractData
                commit_text = extractCommitText(prev_commit_sha)
                if commit_text:
                    treeSHA, _, _, _ = extractDataCommit(commit_text)
                    root_tree_path = os.path.join(assvc_path, "objects", treeSHA[:2], treeSHA)
                    with open(root_tree_path, "rb") as f:
                        tree_data = zlib.decompress(f.read())
                    
                    stack = extractDataTree(tree_data.decode())
                    while stack:
                        entry_type, name, sha = stack.pop()
                        object_data = extractData(sha)
                        if isinstance(object_data, str):
                            object_data = object_data.encode()
                        
                        if entry_type == "16384":
                            children = extractDataTree(object_data.decode())
                            for (child_type, child_name, child_sha) in reversed(children):
                                full_name = os.path.join(name, child_name) if name else child_name
                                if child_type != "16384": 
                                    abs_path = os.path.join(parent_path, full_name)
                                    previous_commit_files[os.path.abspath(abs_path)] = (child_sha, child_type)
                                else:
                                    stack.append((child_type, full_name, child_sha))
                        else:  
                            abs_path = os.path.join(parent_path, name)
                            previous_commit_files[os.path.abspath(abs_path)] = (sha, entry_type)
            except Exception as e:
                
                pass
        
        for root, dirs, files in os.walk(parent_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
            rel_root = os.path.relpath(root, parent_path)
            if rel_root == '.':
                rel_root = ""
            
            blob_list = []
            for file in files:
                file = os.path.normpath(file)
                if file in ignore_files:
                    continue
                abs_path = os.path.abspath(os.path.join(root, file))
                

                if abs_path in commitSet:
                    file_path = os.path.join(root, file)
                    if not os.path.isfile(file_path):
                        continue
                    try:
                        shaName, mode = make_blob(file_path, assvc_path)
                        blob_entry = f"{mode} {file} {shaName}"
                        blob_list.append(blob_entry)
                    except Exception as e:
                        print(f"Warning: Skipping file {file_path} - unable to process")
                        continue

                elif abs_path in previous_commit_files and os.path.exists(abs_path):
                    old_sha, old_mode = previous_commit_files[abs_path]
                    blob_entry = f"{old_mode} {file} {old_sha}"
                    blob_list.append(blob_entry)

            blobs_by_parent[rel_root] = blob_list
        
            dir_list = []
            for d in dirs:
                if d in ignore_dirs:
                    continue
                dir_path = os.path.join(root, d)
                dir_list.append(d)
        
                if is_dir_empty(dir_path):
                    try:
                        if os.path.abspath(dir_path) not in commitSet:
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
        clear()
    except PermissionError:
        print("Error: Permission denied. Unable to access files for commit.")
    except Exception as e:
        print("Error: An unexpected error occurred during commit.")

def make_blob(file_path, assvc_path):
    try:
        with open(file_path, "rb") as f:
            file_content = f.read()

        size = len(file_content)
        header = f"blob {size}\n".encode()
        blob_content = header + file_content

        sha = hashlib.sha1(blob_content).hexdigest()
        compressed = zlib.compress(blob_content)

        first_two = sha[:2]
        objects_dir = os.path.join(assvc_path, "objects", first_two)
        os.makedirs(objects_dir, exist_ok=True)

        blob_path = os.path.join(objects_dir, sha)
        with open(blob_path, "wb") as f:
            f.write(compressed)

        st = os.stat(file_path)
        mode = st.st_mode & 0o777
        #print(f"Created blob for {file_path} with SHA: {sha}")
        return sha, mode

    except Exception:
        raise Exception(f"Cannot read file: {file_path}")


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


def save_history(assvc_path, sha):
    try:
        with open(get_history(assvc_path), "a") as f:
            f.write(sha + '\n')
    except IOError:
        print("Warning: Could not save history")





