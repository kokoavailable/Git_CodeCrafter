import sys
import os
import zlib

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
    print(content.decode())


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
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
