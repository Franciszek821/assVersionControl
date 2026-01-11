import os

import time
import zlib
from assvcPackage.commit import find_assvc


def printHistory():
    assvc_path = find_assvc()
    history_path = os.path.join(assvc_path, "history", "history")
    if not os.path.exists(history_path):
        print("No history found.")
        return

    with open(history_path, "r") as f:
        commits = f.readlines()

    print("History:" + '\n')
    for commit_sha in commits:
        description = getTextDescription(commit_sha.strip(), assvc_path)
        print(f"Commit: {commit_sha.strip()}")
        print(f"    Description: {description}")

def getTextDescription(sha, assvc_path):
    commit_path = os.path.join(assvc_path, "objects", sha[:2], sha)
    with open(commit_path, "rb") as f:
        compressed_data = f.read()
    decompressed = zlib.decompress(compressed_data)
    commit_text = decompressed.decode("utf-8", errors="replace")
    return extractDataCommit(commit_text)


def extractDataCommit(commit_content):
    lines = commit_content.strip().splitlines()
    lines[0].split(" ", 1)[1]

    commiter_parts = lines[1].split(" ")
    commiter = commiter_parts[1]
    timestamp = commiter_parts[2]
    formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(timestamp)))

    message = "\n".join(lines[3:])

    return message, formatted_time, commiter