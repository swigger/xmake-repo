#!/usr/bin/env python
# coding:utf8 vim:ts=4


"""
1. https://xmake.io/llms-full.txt  grep "url: /zh/" got all urls.
    ignore /zh/about/* /zh/posts/*
2. for each link, download it. save to xmake-skill/
   retry 3 times if net failed. only write to final filename when successfully downloaded.
"""

import os
import re
import time
import urllib.request
import urllib.error

BASE_URL = "https://xmake.io/llms-full.txt"
DOC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "xmake-skill")
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


def fetch_with_retry(url, retries=MAX_RETRIES):
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "xmake-doc-fetcher/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8-sig")
        except (urllib.error.URLError, OSError) as e:
            print(f"  attempt {attempt}/{retries} failed: {e}")
            if attempt < retries:
                time.sleep(RETRY_DELAY * attempt)
    return None


def parse_sections(text):
    """Parse llms-full.txt into (url_path, content) pairs."""
    # split by the --- url: ... --- frontmatter blocks
    # pattern: ---\nurl: /some/path.md\n---\n<content>
    parts = re.split(r"^---\s*$", text, flags=re.MULTILINE)
    sections = []
    i = 0
    while i < len(parts):
        block = parts[i].strip()
        m = re.match(r"url:\s*(\S+)", block)
        if m:
            url_path = m.group(1)
            content = parts[i + 1] if i + 1 < len(parts) else ""
            sections.append((url_path, content.strip()))
            i += 2
        else:
            i += 1
    return sections


def should_keep(url_path):
    """Keep /zh/ urls, but ignore /zh/about/* and /zh/posts/*."""
    if not url_path.startswith("/zh/"):
        return False
    if url_path.startswith("/zh/about/") or url_path.startswith("/zh/posts/") or url_path.startswith("/zh/blog.md"):
        return False
    return True


def save_section(url_path, content):
    """Save content to xmake-skill/<url_path>. Write to tmp first, rename on success."""
    rel = url_path.lstrip("/")
    dest = os.path.join(DOC_DIR, rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = dest + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(content)
            f.write("\n")
        os.replace(tmp, dest)
        return True
    except OSError as e:
        print(f"  write error: {e}")
        if os.path.exists(tmp):
            os.remove(tmp)
        return False


def main():
    print(f"Fetching {BASE_URL} ...")
    text = fetch_with_retry(BASE_URL)
    if text is None:
        print("Failed to download llms-full.txt after retries, aborting.")
        return

    sections = parse_sections(text)
    targets = [(u, c) for u, c in sections if should_keep(u)]
    print(f"Found {len(sections)} total sections, {len(targets)} zh docs to save (excluding about/posts).")

    ok, fail = 0, 0
    for i, (url_path, content) in enumerate(targets, 1):
        print(f"[{i}/{len(targets)}] {url_path}")
        if save_section(url_path, content):
            ok += 1
        else:
            fail += 1

    print(f"\nDone. saved={ok}, failed={fail}")


if __name__ == "__main__":
    main()
