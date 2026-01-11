import getpass
import os
import hashlib
import zlib
import time



config_path = os.path.expanduser("~/.config/assvc/config")

def depth(parent):
    return 0 if parent == "" else parent.count(os.sep) + 1



def commit(message):
    assvc_path = find_assvc()
    if assvc_path is None:
        print("Error: not an assvc repository (run `assvc start` first)dddd")
        return

    parent_path = os.path.dirname(assvc_path)

        
    
    ignore_dirs, ignore_files = get_ignore(parent_path)
    blobs_by_parent = {}
    dir_by_parent = {}
    item_by_parent = {}
    tree_sha = {}

    for root, dirs, files in os.walk(parent_path):
        # ignore .assvc or any other dirs
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
    
        # relative path of current folder
        rel_root = os.path.relpath(root, parent_path)  # '.' for root, else 'dupa', 'dupa/chuj', etc.
        if rel_root == '.':
            rel_root = ""
        

    
        # --- process files ---
        blob_list = []
        for file in files:
            if file in ignore_files:
                continue
            file_path = os.path.join(root, file)
            if not is_text_file(file_path):
                continue
            shaName, mode = make_blob(file_path, assvc_path)
            rel_file_path = os.path.relpath(file_path, parent_path)
            blob_entry = f"{mode} {file} {shaName}"
            blob_list.append(blob_entry)

    
        blobs_by_parent[rel_root] = blob_list  # save all blobs for this folder
    
        # --- process subdirectories ---
        dir_list = []
        for d in dirs:
            if d in ignore_dirs:
                continue
            dir_path = os.path.join(root, d)
            dir_list.append(d)
    
            # if directory is empty, create an empty tree for it
            if os.path.isdir(dir_path) and not os.listdir(dir_path):
                make_tree_empty_dir(os.path.relpath(dir_path, parent_path), assvc_path, tree_sha)
    
        dir_by_parent[rel_root] = dir_list  # save all subdirectories for this folder




    for parent in blobs_by_parent.keys():  # or dir_by_parent.keys() if they match
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

def get_first_parent(file_path, repo_root):


    rel_path = os.path.relpath(file_path, repo_root)
    

    if rel_path == '.' or os.sep not in rel_path:
        return ''
    
    # otherwise, return the first folder in the path
    return rel_path.split(os.sep)[0]
            
def make_blob(file_path, assvc_path):

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
    
    st = os.stat(blob_path)
    mode = st.st_mode & 0o777
    return sha, mode
                

def make_tree(parent, blob, directory, assvc_path, tree_sha):
    
    mode = 0o40000
    parentContent = []
    for b in blob:
        b_content = f"{b}\n"
        parentContent.append(b_content)
    for d in directory:
        # Resolve child's full relative key (use parent if not root)
        child_key = os.path.join(parent, d) if parent else d
        child_shas = tree_sha.get(child_key)
        child_ref = child_shas[-1] if child_shas else ""
        d_content = f"{mode} {d} {child_ref}\n"
        parentContent.append(d_content)
    
    sha = hashlib.sha1("".join(parentContent).encode()).hexdigest()
    compressed = zlib.compress("".join(parentContent).encode())
    first_two = sha[:2]
    os.makedirs(assvc_path + "/objects/" + first_two, exist_ok=True)
    parent_path = assvc_path + "/objects/" + first_two + "/" + sha
    with open(parent_path, "wb") as f:
        f.write(compressed)


    if parent == "":
        return sha
        
    tree_sha.setdefault(parent, []).append(sha)


def make_tree_empty_dir(dir, assvc_path, tree_sha):
    mode = 0o40000
    tree_content = b""  # no entries
    dirContent = b"tree " + str(len(tree_content)).encode() + b"\0" + tree_content
    
    sha = hashlib.sha1(dirContent).hexdigest()
    compressed = zlib.compress(dirContent)
    first_two = sha[:2]
    os.makedirs(assvc_path + "/objects/" + first_two, exist_ok=True)
    parent_path = assvc_path + "/objects/" + first_two + "/" + sha
    with open(parent_path, "wb") as f:
        f.write(compressed)


    tree_sha.setdefault(dir, []).append(sha)
    return sha

def make_commit(tree_root_sha, assvc_path, message):
    os.makedirs(os.path.join(assvc_path, 'head'), exist_ok=True)

    commiter = user = getpass.getuser()
    timestamp = int(time.time())
    commit_content = f"tree {tree_root_sha}\ncommiter {commiter} {timestamp}\n\n{message}\n"
    sha = hashlib.sha1(commit_content.encode()).hexdigest()
    compressed = zlib.compress(commit_content.encode())
    first_two = sha[:2]
    os.makedirs(assvc_path + "/objects/" + first_two, exist_ok=True)
    commit_path = assvc_path + "/objects/" + first_two + "/" + sha
    with open(commit_path, "wb") as f:
        f.write(compressed)
    print(f"Commit created Message: {message} SHA: {sha}")
    with open(assvc_path + '/head/current', "w") as f:
        f.write(sha)
    save_history(assvc_path, sha)
    return sha
    






def is_text_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            f.read()
        return True
    except (UnicodeDecodeError, OSError):
        return False

def find_assvc():
    assvc_path = os.path.join(os.getcwd(), ".assvc")
    return assvc_path if os.path.exists(assvc_path) else None


def save_history(assvc_path, sha):
    with open(assvc_path + '/history/history', "a") as f:
        f.write(sha + '\n')


def get_ignore(parent_path):
    ignore_files = set()
    ignore_dirs = {'.assvc', '.git', '__pycache__'}

    assignore_path = os.path.join(parent_path, ".assignore")
    if not os.path.isfile(assignore_path):
        return ignore_dirs, ignore_files

    with open(assignore_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # skip comments and empty lines
            if not line or line.startswith("#"):
                continue

            # folders must start with /
            if line.startswith("/"):
                ignore_dirs.add(line.lstrip("/"))
            else:
                ignore_files.add(line)

    return ignore_dirs, ignore_files

        





