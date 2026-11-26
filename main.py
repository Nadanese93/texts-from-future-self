#!/usr/bin/env python3
"""Texts From Your Future Self — Make.fun micro bounty entry.

Writes a single text message from the future self to /output/entry.txt.
"""

import hashlib
import os
import sys
import unicodedata

ENTRY = (
    "Future you. Turn off autocorrect NOW. In 2041 it changes 'ducking' "
    "to the other word in a text to my boss's boss. Twice. I still work "
    "there. Barely."
)

EXPECTED_SHA256 = (
    "ca31fa653a0ce85fba9d69e0a257951a34e97abd5b6629251e052be446ed8c92"
)


def verify(path: str) -> bool:
    """Read /output/entry.txt back from disk and validate it.

    Returns True only if the on-disk bytes are exactly the canonical
    UTF-8 encoding of ENTRY: 1-200 chars, a single line with no newline,
    no control characters, exact byte length, and matching sha256.
    Prints a diagnostic to stderr and returns False otherwise.
    """
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError as exc:
        print(f"verify: cannot read {path}: {exc}", file=sys.stderr)
        return False
    expected = ENTRY.encode("utf-8")
    if len(data) != len(expected):
        print(
            f"verify: size mismatch: got {len(data)} bytes, "
            f"expected {len(expected)}",
            file=sys.stderr,
        )
        return False
    if hashlib.sha256(data).hexdigest() != EXPECTED_SHA256:
        print("verify: sha256 mismatch", file=sys.stderr)
        return False
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        print(f"verify: not valid UTF-8: {exc}", file=sys.stderr)
        return False
    if not 1 <= len(text) <= 200:
        print(f"verify: length {len(text)} outside 1-200 chars", file=sys.stderr)
        return False
    if "\n" in text or "\r" in text:
        print("verify: entry must be a single line", file=sys.stderr)
        return False
    for ch in text:
        if ord(ch) < 0x20:
            print(
                f"verify: control character U+{ord(ch):04X} not allowed",
                file=sys.stderr,
            )
            return False
        if unicodedata.category(ch) in ("Cc", "Cf", "Cs", "Co", "Cn"):
            print(
                f"verify: non-printable character U+{ord(ch):04X} "
                f"(category {unicodedata.category(ch)}) not allowed",
                file=sys.stderr,
            )
            return False
    if text != text.rstrip(" "):
        print("verify: trailing space not allowed", file=sys.stderr)
        return False
    return True


def main() -> int:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "wb") as f:
        f.write(ENTRY.encode("utf-8"))
    return 0 if verify(path) else 1


if __name__ == "__main__":
    sys.exit(main())
