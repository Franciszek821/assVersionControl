import os
import time
import zlib
from assvcPackage.commit import find_assvc, shorten_sha, get_history


def printHistory(long):
    try:
        assvc_path = find_assvc()
        if not assvc_path:
            print("Error: .assvc directory not found.")
            return
        

        try:
            with open(get_history(assvc_path), "r") as f:
                commits = f.readlines()
        except IOError:
            print("Error: Unable to read history file.")
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
        print("Error: An unexpected error occurred while reading history.")

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