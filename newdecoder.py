# newdecoder.py

import codecs
import base64
import base58
import re
import argparse
import os
import json
from functools import lru_cache
import sys

# --- Constants and Patterns ---
BASE16_PATTERN = r'(?:^|[^0-9A-Fa-f])([0-9A-Fa-f]{4,})(?:$|[^0-9A-Fa-f])'
BASE32_PATTERN = r'(?:^|[^A-Z2-7=])([A-Z2-7]{4,}=*)(?:$|[^A-Z2-7=])'
BASE58_PATTERN = r'(?:^|[^123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz])([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{4,})(?:$|[^123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz])'
BASE64_PATTERN = r'(?:^|[^A-Za-z0-9+/=])([A-Za-z0-9+/]{4,}={0,2})(?:$|[^A-Za-z0-9+/=])'
BASE85_PATTERN = r'(<~)?([0-9A-Za-z!#$%&()*+\-;<=>?@^_`{|}~]+)(~>)?'

# --- Decoders (with LRU caching for efficiency) ---
@lru_cache(maxsize=1024)
def decode_base16(s):
    try:
        return codecs.decode(s, 'hex').decode('utf-8')
    except:
        return None

@lru_cache(maxsize=1024)
def decode_base32(s):
    try:
        return base64.b32decode(s, casefold=True).decode('utf-8')
    except:
        return None

@lru_cache(maxsize=1024)
def decode_base58(s):
    try:
        return base58.b58decode(s).decode('utf-8')
    except:
        return None

@lru_cache(maxsize=1024)
def decode_base64(s):
    try:
        return base64.b64decode(s).decode('utf-8')
    except:
        return None

@lru_cache(maxsize=1024)
def decode_base85(s):
    try:
        return base64.a85decode(s).decode('utf-8')
    except:
        return None

# --- Core Decoding Logic ---
def decode_from_text(text, min_length=0):
    results = []
    for base_name, pattern, decoder in [
        ("Base16", BASE16_PATTERN, decode_base16),
        ("Base32", BASE32_PATTERN, decode_base32),
        ("Base58", BASE58_PATTERN, decode_base58),
        ("Base64", BASE64_PATTERN, decode_base64),
        ("Base85", BASE85_PATTERN, decode_base85)
    ]:
        matches = re.findall(pattern, text)
        for match in matches:
            if isinstance(match, tuple):
                match = match[1]  # For BASE85 groups
            decoded = decoder(match)
            if decoded and len(decoded) >= min_length:
                results.append({
                    "base": base_name,
                    "encoded": match,
                    "decoded": decoded
                })
    return results

# --- File and Directory Utilities ---
def decode_from_file(file_path, min_length=0):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    return decode_from_text(text, min_length)

def decode_from_directory(directory_path, min_length=0):
    all_results = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".txt"):
                path = os.path.join(root, file)
                results = decode_from_file(path, min_length)
                all_results.append({
                    "file": path,
                    "results": results
                })
    return all_results

def interactive_mode(min_length=0):
    print("Interactive decoding mode (Ctrl+C to exit).")
    try:
        while True:
            text = input("Enter text: ")
            results = decode_from_text(text, min_length)
            print(json.dumps(results, indent=2))
    except KeyboardInterrupt:
        print("\nExiting interactive mode.")

# --- Output Handling ---
def print_results(results, output_file=None):
    output = json.dumps(results, indent=2)
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
    else:
        print(output)

# --- Main Entry Point ---
def main():
    parser = argparse.ArgumentParser(description='Decode base-encoded strings.')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-t', '--text', help='Text input')
    group.add_argument('-f', '--file', help='File path')
    group.add_argument('-d', '--directory', help='Directory path')
    parser.add_argument('-i', '--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('-l', '--min-length', type=int, default=4, help='Min decoded length')
    parser.add_argument('-o', '--output', help='Output JSON file')

    args = parser.parse_args()
    if args.interactive:
        interactive_mode(args.min_length)
        return

    if not args.text and not args.file and not args.directory:
        parser.print_help()
        print("\nError: No input source specified.", file=sys.stderr)
        sys.exit(1)

    try:
        if args.text:
            results = decode_from_tex
