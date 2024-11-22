import sys
import os
import zlib
import hashlib
import time

def init_git():
    os.mkdir(".git")
    os.mkdir(".git/objects")
    os.mkdir(".git/refs")
    with open(".git/HEAD", "w") as f:
        f.write("ref: refs/heads/main\n")
    print("Initialized git directory")

def cat_file(blob_sha):
    obj_dir = f".git/objects/{blob_sha[:2]}"
    obj_file = f"{obj_dir}/{blob_sha[2:]}"

    if not os.path.exists(obj_file):
        print(f"Error: Object {blob_sha} does not exist!", file = sys.stderr)
        sys.exit(1)

    with open(obj_file, "rb") as f:
        compressed_data = f.read()
    decompressed_data = zlib.decompress(compressed_data)

    header_end = decompressed_data.find(b'\0')
    if header_end == -1:
        sys.exit(1)

    content = decompressed_data[header_end + 1:]
    print(content.decode(), end= "")

def write_tree(directory="."):
    s = b""
    for entry in sorted(os.listdir(directory)):
        if entry == ".git":
            continue

        entry_path = os.path.join(directory, entry)

        if os.path.isdir(entry_path):
            mode = "40000"
            sha1 = write_tree(entry_path)
        elif os.path.isfile(entry_path):
            mode = "100644"
            sha1 = hash_object(entry_path, write= True)
        else:
            continue
        
        s += f"{mode} {entry}\0".encode() + bytes.fromhex(sha1)

    tree_content = f"tree {len(s)}\0".encode() + s
    sha1 = hashlib.sha1(tree_content).hexdigest()

    obj_dir = f".git/objects/{sha1[:2]}"
    obj_file = f"{obj_dir}/{sha1[2:]}"
    os.makedirs(obj_dir, exist_ok=True)
    with open(obj_file, "wb") as f:
        f.write(zlib.compress(tree_content))
    
    return sha1




def hash_object(file_path, write=False):
    with open(file_path, "rb") as f:
        content = f.read()

    size = len(content)
    blob = f"blob {size}\0".encode() + content

    sha1 = hashlib.sha1(blob).hexdigest()

    if write:

        object_dir = f".git/objects/{sha1[:2]}"
        object_file = f"{object_dir}/{sha1[2:]}"
        if not os.path.exists(object_dir):
            os.makedirs(object_dir)

        compressed_blob = zlib.compress(blob)

        with open(object_file, "wb") as f:
            f.write(compressed_blob)

    return sha1

def ls_tree(tree_sha):
    object_dir = f".git/objects/{tree_sha[:2]}"
    object_file = f"{object_dir}/{tree_sha[2:]}"

    with open(object_file, "rb") as f:
        compressed_data = f.read()

    decompressed_data = zlib.decompress(compressed_data)
    header_end = decompressed_data.find(b'\0')
    content = decompressed_data[header_end + 1:]

    entries = ""
    offset = 0
    while offset < len(content):
        null_pos = content.find(b'\0', offset)
        
        mode_name = content[offset:null_pos].decode()
        mode, name = mode_name.split(" ", 1)

        sha_start = null_pos + 1
        sha_end = sha_start + 20
        sha = content[sha_start:sha_end]

        entries += f"{name}\n"

        offset = sha_end

    print(entries, end="")

    return entries

def commit_tree(tree_sha, parent_sha = None, author = "", committer = "", message = ""):
    timestamp = int(time.time())
    timezone = '+0000'

    content = f"tree {tree_sha}\n"
    if parent_sha:
        content += f"parent {parent_sha}\n"
        content += f"author {author} {timestamp} {timezone}\n"
        content += f"committer {committer} {timestamp} {timezone}\n\n"
        content += message + "\n"

    size = len(content)
    commit_object = f"commit {size}\0".encode() + content.encode()

    sha1 = hashlib.sha1(commit_object).hexdigest()

    # save_to_git_objects(sha1, commit_object)
    return sha1


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    # Uncomment this block to pass the first stage
    
    command = sys.argv[1]
    if command == "init":
        init_git()
    elif command == "cat-file" and sys.argv[2] == "-p":
        blob_sha = sys.argv[3]
        cat_file(blob_sha)
    elif command == "hash-object" and sys.argv[2] == "-w":
        file_path = sys.argv[3]
        blob_sha = hash_object(file_path, write=True)
        print(blob_sha, end="")
    elif command == "ls-tree" and sys.argv[2] == "--name-only":
        tree_sha = sys.argv[3]
        ls_tree(tree_sha)
    elif command == "write-tree":
        tree_sha = write_tree(".")
        print(tree_sha)
    elif command == "commit-tree":
        tree_sha = sys.argv[2]

        if len(sys.argv) == 5 and sys.argv[3] == "-m":
            message = sys.argv[4]

        elif len(sys.argv) == 7 and sys.argv[3] == "-p" and sys.argv[5] == "-m":
            parent_sha = sys.argv[4]
            message = sys.argv[6]
        else:
            sys.exit(1)

        print(commit_tree(tree_sha, parent_sha, message), end = "")



        




    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
