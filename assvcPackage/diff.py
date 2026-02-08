import os
import hashlib
import zlib
import time
import difflib
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from warning import show_warning

from assvcPackage.utils import (find_assvc, get_ignore, deShorten_sha, get_history, extractDataCommit,
                                 extractDataTree, extractData, show_diff, is_text_bytes, is_text_file)


def diff(commit_sha, file_path, noPrint=False):
    assvc_path = find_assvc()
    if not assvc_path:
        show_warning(None, "Repository Error", ".assvc directory not found.")
        return None
    
    parent_path = os.path.dirname(assvc_path)
    ignore_dirs, ignore_files = get_ignore(parent_path)
    
    file_path = os.path.abspath(file_path)
    try:
        if commit_sha == "latest":
            current_path = os.path.join(find_assvc(), "head/current")
            try:
                with open(current_path, "r") as f:
                    commit_sha = f.read().strip()
            except IOError:
                show_warning(None, "Read Error", "Could not read current commit reference")
                return None
        
        commit_sha = deShorten_sha(commit_sha, get_history(assvc_path))
        
        commit_path = os.path.join(assvc_path, "objects", commit_sha[:2], commit_sha)
        try:
            with open(commit_path, "rb") as f:
                compressed_data = f.read()
        except FileNotFoundError:
            show_warning(None, "Commit Error", f"Commit '{commit_sha}' not found.")
            return None
        except IOError:
            show_warning(None, "Read Error", "Unable to read commit data.")
            return None

        try:
            decompressed = zlib.decompress(compressed_data)
            commit_text = decompressed.decode("utf-8", errors="replace")
        except Exception:
            show_warning(None, "Data Error", "Corrupted commit data.")
            return None

        treeSHA, commiter, timestamp, message = extractDataCommit(commit_text)
        if not noPrint:
            print(f"Comparing with commit: {commiter} {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(timestamp)))}")
            print(f"Message: {message}")


        root_tree_path = os.path.join(assvc_path, "objects", treeSHA[:2], treeSHA)
        try:
            with open(root_tree_path, "rb") as f:
                tree_data = zlib.decompress(f.read())
        except Exception:
            show_warning(None, "Tree Error", "Could not read tree data.")
            return None

        stack = extractDataTree(tree_data.decode())
        path_check = []

        while stack:
            entry_type, name, sha = stack.pop()
            try:
                object_data = extractData(sha)
            except Exception:
                show_warning(None, "Object Warning", f"Could not read object {sha}")
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
            show_warning(None, "File Error", f"File '{file_path}' does not exist in the working directory.")
            return None
        for (path, sha) in path_check:
            if path != os.path.abspath(file_path):
                continue
            else:
                if not noPrint:
                    print(f"\nDifferences for file: {path}\n")
                return check([(path, sha)], noPrint, assvc_path, parent_path, ignore_dirs, ignore_files)
        show_warning(None, "File Error", f"File '{file_path}' not found in the specified commit.")
        return None


    except Exception:
        show_warning(None, "Comparison Error", "An unexpected error occurred during comparison.")
        return None

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
RESET  = "\033[0m"

def check(path_check, noPrint=False, assvc_path=None, parent_path=None, ignore_dirs=None, ignore_files=None):
    if not assvc_path:
        assvc_path = find_assvc()
    if not parent_path:
        parent_path = os.path.dirname(assvc_path)
    if ignore_dirs is None or ignore_files is None:
        ignore_dirs, ignore_files = get_ignore(parent_path)
    
    diff_result = []
    try:
        if not noPrint:
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
                    if not noPrint:
                        print(f"{YELLOW}  MODIFIED:{RESET} {path}")

                    
                    if is_text_bytes(old_content_bytes) and is_text_bytes(now_blob):
                        old_text = old_content_bytes.decode("utf-8", errors="replace")
                        new_text = now_blob.decode("utf-8", errors="replace")
                        
                        # Generate diff lines
                        import difflib
                        old_lines = old_text.splitlines(keepends=True)
                        new_lines = new_text.splitlines(keepends=True)
                        diff_lines = list(difflib.unified_diff(
                            old_lines,
                            new_lines,
                            fromfile=path + " (previous)",
                            tofile=path + " (current)",
                            lineterm=""
                        ))
                        
                        # Print if needed
                        if not noPrint:
                            show_diff(old_text, new_text, path)
                        
                        diff_result.append({
                            'path': path,
                            'status': 'MODIFIED',
                            'old_content': old_text,
                            'new_content': new_text,
                            'diff': diff_lines
                        })
                    else:
                        if not noPrint:
                            print(f"{YELLOW}    MODIFIED (binary, no diff):{RESET} {path}")
                        diff_result.append({
                            'path': path,
                            'status': 'MODIFIED',
                            'binary': True
                        })

            except IOError:
                show_warning(None, "Read Warning", f"Could not read file {path}")
                continue
            except Exception:
                show_warning(None, "Process Warning", f"Could not process file {path}")
                continue

        return diff_result

    except Exception:
        show_warning(None, "Check Error", "An error occurred during comparison check.")
        return diff_result
