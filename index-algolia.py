#!/usr/bin/env python3
"""Index rad.as blog posts to Algolia."""

import json
import os
import re
import urllib.request

ALGOLIA_APP_ID = "T3V96ZTNQJ"
ALGOLIA_ADMIN_KEY = "fa7b1e403de929a2681b0581a26e0f37"
INDEX_NAME = "rad"
BASE_URL = "https://rad.as"

blog_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "blog")
records = []

for filename in sorted(os.listdir(blog_dir)):
    if not filename.endswith(".html") or filename == "index.html":
        continue

    filepath = os.path.join(blog_dir, filename)
    with open(filepath, "r") as f:
        html = f.read()

    # Extract title
    m = re.search(r"<title>(?:Blog - )?(.+?)</title>", html)
    title = m.group(1).strip() if m else filename.replace(".html", "")

    # Extract post content (between <div class="post"> and closing </div> before footer)
    m = re.search(r'<div class="post">(.*?)</div>\s*(?:<footer|<script)', html, re.DOTALL)
    content = m.group(1) if m else ""

    # Strip HTML tags
    content = re.sub(r"<[^>]+>", " ", content)
    # Collapse whitespace
    content = re.sub(r"\s+", " ", content).strip()
    # Truncate to 5000 chars for Algolia
    content = content[:5000]

    permalink = f"{BASE_URL}/blog/{filename}"

    records.append({
        "objectID": filename,
        "title": title,
        "content": content,
        "permalink": permalink,
    })

    print(f"  Indexed: {title}")

print(f"\n{len(records)} posts indexed. Pushing to Algolia index '{INDEX_NAME}'...")

# Clear the index first
clear_req = urllib.request.Request(
    f"https://{ALGOLIA_APP_ID}-dsn.algolia.net/1/indexes/{INDEX_NAME}/clear",
    method="POST",
    headers={
        "X-Algolia-API-Key": ALGOLIA_ADMIN_KEY,
        "X-Algolia-Application-Id": ALGOLIA_APP_ID,
        "Content-Type": "application/json",
    },
    data=b"{}",
)
urllib.request.urlopen(clear_req)

# Batch add all records
batch_body = json.dumps({
    "requests": [{"action": "addObject", "body": r} for r in records]
}).encode()

batch_req = urllib.request.Request(
    f"https://{ALGOLIA_APP_ID}-dsn.algolia.net/1/indexes/{INDEX_NAME}/batch",
    method="POST",
    headers={
        "X-Algolia-API-Key": ALGOLIA_ADMIN_KEY,
        "X-Algolia-Application-Id": ALGOLIA_APP_ID,
        "Content-Type": "application/json",
    },
    data=batch_body,
)
response = urllib.request.urlopen(batch_req)
result = json.loads(response.read())
print(f"Algolia response: {len(result.get('objectIDs', []))} objects indexed.")

# Configure searchable attributes
settings_body = json.dumps({
    "searchableAttributes": ["title", "content"],
    "attributesToHighlight": ["title"],
    "attributesToSnippet": ["content:30"],
}).encode()

settings_req = urllib.request.Request(
    f"https://{ALGOLIA_APP_ID}-dsn.algolia.net/1/indexes/{INDEX_NAME}/settings",
    method="PUT",
    headers={
        "X-Algolia-API-Key": ALGOLIA_ADMIN_KEY,
        "X-Algolia-Application-Id": ALGOLIA_APP_ID,
        "Content-Type": "application/json",
    },
    data=settings_body,
)
urllib.request.urlopen(settings_req)

print("Search settings configured. Done!")
