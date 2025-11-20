import zlib


def decode_commit(compressed_bytes):
    """
    Decompress a commit object and return its content as text.
    """
    decompressed = zlib.decompress(compressed_bytes)
    # For your assvc commit, there is no Git-style "commit<size>\0" header,
    # just the plain commit_content you wrote.
    try:
        return decompressed.decode("utf-8")
    except UnicodeDecodeError:
        return decompressed  # if somehow binary

# Example usage:
# Suppose you have the path to a commit object
commit_file = "/home/franekdomanski/Documents/Programing/assVersionControl/.assvc/objects/6b/6b88636a64098789b4d0d2505fd7875effc869ba"  # your SHA path
with open(commit_file, "rb") as f:
    compressed_data = f.read()


content = decode_commit(compressed_data)
print("Commit content:\n", content)