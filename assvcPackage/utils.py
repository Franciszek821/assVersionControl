import os
import zlib
import os
import hashlib
import zlib
import time
import difflib

import requests



def find_assvc():
    try:
        assvc_path = os.path.join(os.getcwd(), ".assvc")
        return assvc_path if os.path.exists(assvc_path) else None
    except Exception:
        print("Error: Unable to locate .assvc directory.")
        return None
    
assvc_path = find_assvc()

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

def get_history(assvc_path):
    history_path = os.path.join(assvc_path, "history", "history")
    return history_path

def is_text_bytes(data):
    try:
        data.decode('utf-8')
        return True
    except UnicodeDecodeError:
        return False
    
def is_text_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            f.read()
        return True
    except (UnicodeDecodeError, OSError):
        return False
    
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

def extractCommitText(commit_sha):
    
    commit_sha = deShorten_sha(commit_sha, get_history(assvc_path))

    if not assvc_path:
        print("Error: .assvc directory not found.")
        return
    
    commit_path = os.path.join(assvc_path, "objects", commit_sha[:2], commit_sha)
    try:
        with open(commit_path, "rb") as f:
            compressed_data = f.read()
        try:
            decompressed = zlib.decompress(compressed_data)
            commit_text = decompressed.decode("utf-8", errors="replace")
            return commit_text
        except Exception:
            print("Error: Corrupted commit data.")
            return None
    except FileNotFoundError:
        print(f"Error: Commit '{commit_sha}' not found.")
        return None
    except IOError:
        print("Error: Unable to read commit data.")
        return None
    



def show_diff(old_text, new_text, filename):
    try:
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
                print("\033[32m" + line + "\033[0m")
            elif line.startswith("-") and not line.startswith("---"):
                print("\033[31m" + line + "\033[0m")
    except Exception:
        print(f"Warning: Could not generate diff for {filename}")

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

def read_index(assvc_path):
    index_path = os.path.join(assvc_path, "index")

    if not os.path.exists(index_path):
        return []

    with open(index_path, "r") as f:
        return [line.strip() for line in f if line.strip()]


def is_dir_empty(path):
    return os.path.isdir(path) and not os.listdir(path)

def latest_release(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    r = requests.get(url, timeout=10)

    if r.status_code != 200:
        raise RuntimeError(f"GitHub API error: {r.status_code}")

    data = r.json()
    return {
        "tag": data["tag_name"],
        "name": data["name"],
        "published_at": data["published_at"]
    }

#print(latest_release("Franciszek821", "assVersionControl"))
