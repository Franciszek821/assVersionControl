import os
import time
import zlib
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from warning import show_warning
from assvcPackage.utils import find_assvc, shorten_sha, get_history, extractDataCommit as extractDataCommitUtils, extractDataTree, extractData


def printHistory(long):
    try:
        assvc_path = find_assvc()
        if not assvc_path:
            show_warning(None, "Repository Error", ".assvc directory not found.")
            return
        

        try:
            with open(get_history(assvc_path), "r") as f:
                commits = f.readlines()
        except IOError:
            show_warning(None, "History Error", "Unable to read history file.")
            return

        if not commits:
            print("No commits yet.")
            return

        print("History:" + '\n')
        for commit_sha in commits:
            try:
                description = getTextDescription(commit_sha.strip(), assvc_path)
                short_sha = shorten_sha(commit_sha.strip(), get_history(assvc_path))
                if long:
                    print(f"Commit: {commit_sha.strip()}")
                else:
                    print(f"Commit: {short_sha}")
                print(f"    Description: {description}")
            except Exception:
                print(f"Commit: {commit_sha.strip()}")
                print(f"    Description: [Unable to read]")
    except Exception:
        show_warning(None, "History Error", "An unexpected error occurred while reading history.")

def getTextDescription(sha, assvc_path):
    try:
        commit_path = os.path.join(assvc_path, "objects", sha[:2], sha)
        if not os.path.exists(commit_path):
            raise FileNotFoundError(f"Commit {sha} not found")
        
        with open(commit_path, "rb") as f:
            compressed_data = f.read()
        decompressed = zlib.decompress(compressed_data)
        commit_text = decompressed.decode("utf-8", errors="replace")
        return extractDataCommit(commit_text)
    except FileNotFoundError:
        raise Exception(f"Commit not found")
    except IOError:
        raise Exception("Unable to read commit data")
    except Exception:
        raise Exception("Corrupted commit data")

def extractDataCommit(commit_content):
    try:
        lines = commit_content.strip().splitlines()
        lines[0].split(" ", 1)[1]

        commiter_parts = lines[1].split(" ")
        commiter = commiter_parts[1]
        timestamp = commiter_parts[2]
        formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(timestamp)))

        message = "\n".join(lines[3:])

        return message, formatted_time, commiter
    except (IndexError, ValueError):
        raise Exception("Corrupted commit format")

def isPathInHistory(path):

    try:
        assvc_path = find_assvc()
        if not assvc_path:
            return False
        
        parent_path = os.path.dirname(assvc_path)
        
        if os.path.isabs(path):
            rel_path = os.path.relpath(path, parent_path)
        else:
            rel_path = path
        
        try:
            with open(get_history(assvc_path), "r") as f:
                commits = [line.strip() for line in f if line.strip()]
        except IOError:
            return False
        
        if not commits:
            return False
        
        for commit_sha in commits:
            try:
                commit_path = os.path.join(assvc_path, "objects", commit_sha[:2], commit_sha)
                with open(commit_path, "rb") as f:
                    compressed_data = f.read()
                decompressed = zlib.decompress(compressed_data)
                commit_text = decompressed.decode("utf-8", errors="replace")
                
                tree_sha, _, _, _ = extractDataCommitUtils(commit_text)
                
                if _find_path_in_tree(tree_sha, rel_path):
                    return True
            except Exception:
                continue
        
        return False
    except Exception:
        return False

def _find_path_in_tree(tree_sha, target_path):
    """
    Helper function to recursively search for a path in a tree.
    
    Args:
        tree_sha: SHA of the tree to search
        target_path: Path to search for (relative)
        
    Returns:
        bool: True if path found, False otherwise
    """
    try:
        parts = target_path.split(os.sep)
        
        # Get tree data
        tree_data = extractData(tree_sha)
        if isinstance(tree_data, bytes):
            tree_data = tree_data.decode()
        
        entries = extractDataTree(tree_data)
        
        if len(parts) == 1:
            for entry_type, name, sha in entries:
                if name == parts[0]:
                    return True
            return False
        
        for entry_type, name, sha in entries:
            if entry_type == "16384" and name == parts[0]:
                remaining_path = os.sep.join(parts[1:])
                return _find_path_in_tree(sha, remaining_path)
        
        return False
    except Exception:
        return False
    
def howManyCommits(repository_path=None):
    try:
        if repository_path:
            assvc_path = find_assvc(repository_path)
        else:
            assvc_path = find_assvc()
            
        if not assvc_path:
            return 0
        
        try:
            with open(get_history(assvc_path), "r") as f:
                commits = [line.strip() for line in f if line.strip()]
        except IOError:
            return 0
        
        return len(commits)
    except Exception:
        return 0

def getCommits(repository_path=None):
    """
    Returns a list of commit SHAs with their descriptions.
    
    Args:
        repository_path: Optional path to repository. Uses current directory if not provided.
        
    Returns:
        List of tuples: [(sha, message, timestamp, commiter), ...]
    """
    try:
        if repository_path:
            assvc_path = find_assvc(repository_path)
        else:
            assvc_path = find_assvc()
            
        if not assvc_path:
            return []
        
        try:
            with open(get_history(assvc_path), "r") as f:
                commits = [line.strip() for line in f if line.strip()]
        except IOError:
            return []
        
        result = []
        for commit_sha in commits:
            try:
                message, timestamp, commiter = getTextDescription(commit_sha, assvc_path)
                result.append((commit_sha, message, timestamp, commiter))
            except Exception:
                result.append((commit_sha, "[Unable to read]", "", ""))
        
        return result
    except Exception:
        return []