#!/usr/bin/env python3
"""Export one Notion page subtree to versioned Markdown files.

Only descendants of ROOT_PAGE_ID are exported. No AI is called.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
import time
import unicodedata
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_BASE = "https://api.notion.com/v1"
API_VERSION = "2026-03-11"
DEFAULT_ROOT_ID = "3e29b429-9e61-816a-96ca-d16cbd4d2ca4"
OUTPUT_DIR = Path(__file__).resolve().parent / "notes"
MAX_PAGES = 500
MAX_DEPTH = 12


class NotionClient:
    def __init__(self, token: str):
        if not token:
            raise ValueError("NOTION_API_KEY is required")
        self.token = token

    def get(self, path: str, query: dict[str, str | int] | None = None) -> dict:
        return self.request(path, query=query)

    def request(self, path: str, query=None, payload=None) -> dict:
        url = API_BASE + path
        if query:
            url += "?" + urlencode(query)
        request = Request(url, data=None if payload is None else json.dumps(payload).encode("utf-8"), headers={
            "Authorization": "Bearer " + self.token,
            "Notion-Version": API_VERSION,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "atcoder-notion-sync/1.0",
        })
        for attempt in range(6):
            try:
                with urlopen(request, timeout=45) as response:
                    return json.load(response)
            except HTTPError as error:
                body = error.read().decode("utf-8", "replace")[:800]
                if error.code not in (429, 500, 502, 503, 504) or attempt == 5:
                    raise RuntimeError(f"Notion API HTTP {error.code}: {body} ({path})") from error
                retry_after = error.headers.get("Retry-After", "")
                try:
                    delay = min(60.0, max(1.0, float(retry_after)))
                except ValueError:
                    delay = min(30, 2 ** attempt)
                time.sleep(delay)
            except (URLError, TimeoutError) as error:
                if attempt == 5:
                    raise RuntimeError(f"Notion API network error: {error} ({path})") from error
                time.sleep(min(30, 2 ** attempt))
        raise AssertionError("unreachable")

    def children(self, page_id: str):
        cursor = None
        while True:
            query = {"page_size": 100}
            if cursor:
                query["start_cursor"] = cursor
            data = self.get(f"/blocks/{page_id}/children", query)
            for block in data["results"]:
                yield block
            if not data.get("has_more"):
                break
            cursor = data.get("next_cursor")
            if not cursor:
                raise RuntimeError("Pagination indicated has_more but had no next_cursor")

    def database_pages(self, database_id: str):
        database = self.get(f"/databases/{database_id}")
        sources = database.get("data_sources")
        if not isinstance(sources, list) or not sources:
            raise RuntimeError(f"Missing data sources for database {database_id}")
        for source in sources:
            source_id = clean_id(source["id"])
            cursor = None
            cursors = set()
            while True:
                payload = {"page_size": 100}
                if cursor:
                    payload["start_cursor"] = cursor
                data = self.request(f"/data_sources/{source_id}/query", payload=payload)
                for page in data["results"]:
                    if page.get("object") != "page":
                        raise RuntimeError(f"Unexpected query result in data source {source_id}")
                    if not page.get("archived") and not page.get("in_trash"):
                        yield page
                if not data.get("has_more"):
                    break
                cursor = data.get("next_cursor")
                if not cursor or cursor in cursors:
                    raise RuntimeError(f"Invalid pagination in data source {source_id}")
                cursors.add(cursor)

    def markdown(self, page_id: str) -> str:
        response = self.get(f"/pages/{page_id}/markdown")
        if response.get("truncated") or response.get("unknown_block_ids"):
            raise RuntimeError(f"Notion page {page_id} was truncated/inaccessible; refusing partial export")
        content = response.get("markdown")
        if not isinstance(content, str):
            raise RuntimeError(f"Missing markdown for Notion page {page_id}")
        return content


def clean_id(value: str) -> str:
    compact = value.strip().replace("-", "").lower()
    if not re.fullmatch(r"[0-9a-f]{32}", compact):
        raise ValueError("ROOT_PAGE_ID must be a Notion page UUID")
    return "-".join((compact[:8], compact[8:12], compact[12:16], compact[16:20], compact[20:]))


def filename(title: str, page_id: str) -> str:
    title = unicodedata.normalize("NFKC", title)
    title = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", title)
    title = re.sub(r"\s+", "_", title).strip("._ ")[:70].rstrip("._ ")
    if not title:
        title = "untitled"
    return f"{title}-{page_id.replace('-', '')[:8]}"


def page_url(page_id: str) -> str:
    return "https://www.notion.so/" + page_id.replace("-", "")


def export(client: NotionClient, root_id: str, output: Path) -> int:
    """Atomic-ish export: write to staging; replace notes only on full success."""
    root_id = clean_id(root_id)
    staging = output.with_name(output.name + "-staging")
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    count = 0
    lines = ["# 競技プログラミング Snippets (Notion mirror)", "",
             "Source: " + page_url(root_id), "",
             "This directory is generated by GitHub Actions. Edit Notion, not these files.", ""]
    seen: dict[str, Path] = {}

    def visit(page_id: str, title: str, parents: tuple[str, ...], depth: int):
        nonlocal count
        if page_id in seen:
            lines.append(f"{'  ' * depth}- [{title}](<{seen[page_id].as_posix()}>)")
            return
        count += 1
        if count > MAX_PAGES or depth > MAX_DEPTH:
            raise RuntimeError("Exceeded MAX_PAGES/MAX_DEPTH; review export scope")
        stem = filename(title, page_id)
        relative_file = Path(*parents) / (stem + ".md")
        seen[page_id] = relative_file
        page_markdown = client.markdown(page_id)
        destination = staging / relative_file
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            f"# {title}\n\nSource: {page_url(page_id)}\n\n---\n\n" +
            page_markdown.rstrip() + "\n", encoding="utf-8"
        )
        indent = "  " * depth
        lines.append(f"{indent}- [{title}](<{relative_file.as_posix()}>)")
        folder = parents + (stem,)
        for block in client.children(page_id):
            if block.get("type") == "child_page":
                child_title = block.get("child_page", {}).get("title", "Untitled")
                visit(clean_id(block["id"]), child_title, folder, depth + 1)
            elif block.get("type") == "child_database":
                database_id = clean_id(block["id"])
                database_title = block.get("child_database", {}).get("title") or "Untitled database"
                database_folder = folder + (filename(database_title, database_id),)
                lines.append(f"{'  ' * (depth + 1)}- {database_title} (database)")
                pages = {}
                for page in client.database_pages(database_id):
                    pid = clean_id(page["id"])
                    pages.setdefault(pid, page)
                    if len(set(pages) | set(seen)) > MAX_PAGES:
                        raise RuntimeError("Exceeded MAX_PAGES; review export scope")
                # Stable ordering independent of database view order.
                for page in (pages[pid] for pid in sorted(pages)):
                    page_title = "Untitled"
                    for prop in page.get("properties", {}).values():
                        if prop.get("type") == "title":
                            page_title = "".join(part.get("plain_text", part.get("text", {}).get("content", ""))
                                                 for part in prop.get("title", [])) or "Untitled"
                            break
                    visit(clean_id(page["id"]), page_title, database_folder, depth + 2)

    try:
        visit(root_id, "競技プログラミング Snippets", (), 0)
        (staging / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        # Complete snapshot or no replacement; GitHub commits only changed files.
        if output.exists():
            shutil.rmtree(output)
        staging.rename(output)
        return count
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def main() -> None:
    token = os.environ.get("NOTION_API_KEY", "")
    root_id = os.environ.get("ROOT_PAGE_ID", DEFAULT_ROOT_ID)
    client = NotionClient(token)
    count = export(client, root_id, OUTPUT_DIR)
    print(f"Synced {count} Notion pages into {OUTPUT_DIR}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
