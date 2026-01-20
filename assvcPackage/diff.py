import os
import hashlib
import zlib
import time
import difflib

from assvcPackage.utils import (find_assvc, get_ignore, deShorten_sha, get_history, extractDataCommit,
                                 extractDataTree, extractData, show_diff, is_text_bytes, is_text_file)

assvc_path = find_assvc()
if assvc_path:
    parent_path = os.path.dirname(assvc_path)
    ignore_dirs, ignore_files = get_ignore(parent_path)


def diff(commit_sha, file_path):
    file_path = os.path.abspath(file_path)
    try:
        if commit_sha == "latest":
            current_path = os.path.join(find_assvc(), "head/current")
            try:
                with open(current_path, "r") as f:
                    commit_sha = f.read().strip()
            except IOError:
                print("Error: Could not read current commit reference")
                return
        
        commit_sha = deShorten_sha(commit_sha, get_history(assvc_path))

        if not assvc_path:
            print("Error: .assvc directory not found.")
            return
        
        commit_path = os.path.join(assvc_path, "objects", commit_sha[:2], commit_sha)
        try:
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
        print(f"Comparing with commit: {commiter} {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(timestamp)))}")
        print(f"Message: {message}")


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
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' does not exist in the working directory.")
            return
        for (path, sha) in path_check:
            if path != os.path.abspath(file_path):
                continue
            else:
                print(f"\nDifferences for file: {path}\n")
                check([(path, sha)])
                return
        print(f"Error: File '{file_path}' not found in the specified commit.")
        return


    except Exception:
        print("Error: An unexpected error occurred during comparison.")

# colors
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
RESET  = "\033[0m"

def check(path_check):

    try:
        print()

        dirsFilesAll = []
        for root, dirs, files in os.walk(parent_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for f in files:
                if f in ignore_files:
                    continue
                dirsFilesAll.append(os.path.join(root, f))

        for (path, sha) in path_check:


            if not is_text_file(path):
                continue

            try:
                size = os.path.getsize(path)
                with open(path, "rb") as f:
                    fileContent = f.read()

                shapath = os.path.join(assvc_path, "objects", sha[:2], sha)
                with open(shapath, "rb") as f:
                    compressed = f.read()

                old_blob_full = zlib.decompress(compressed)
                header_end = old_blob_full.find(b'\n')
                old_content_bytes = old_blob_full[header_end+1:]


                now_blob_full = b"blob " + str(len(fileContent)).encode() + b"\n" + fileContent 
                shaNow = hashlib.sha1(now_blob_full).hexdigest()


                now_blob = fileContent

                if shaNow != sha:
                    print(f"{YELLOW}  MODIFIED:{RESET} {path}")

                    
                    if is_text_bytes(old_content_bytes) and is_text_bytes(now_blob):
                        old_text = old_content_bytes.decode("utf-8", errors="replace")
                        new_text = now_blob.decode("utf-8", errors="replace")
                        show_diff(old_text, new_text, path)
                    else:
                        print(f"{YELLOW}    MODIFIED (binary, no diff):{RESET} {path}")

            except IOError:
                print(f"Warning: Could not read file {path}")
                continue
            except Exception:
                print(f"Warning: Could not process file {path}")
                continue



    except Exception:
        print("Error: An error occurred during comparison check.")
