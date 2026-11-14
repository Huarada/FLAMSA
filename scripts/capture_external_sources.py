"""Archive registered external sources without interpreting scientific claims."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify

TIMEOUT_SECONDS = 30


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def extract_markdown(
    content: bytes, url: str, requested_selector: str | None = None
) -> tuple[str, str | None, str]:
    soup = BeautifulSoup(content, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else None
    selectors = (requested_selector,) if requested_selector else (".entry-content", "main", "article", "#content")
    selector = next((candidate for candidate in selectors if soup.select_one(candidate)), None)
    if selector is None:
        raise ValueError("No recognizable main content container; manual review required")
    container = BeautifulSoup("<div></div>", "html.parser").div
    assert container is not None
    for selected in soup.select(selector):
        container.append(selected.extract())
    for element in container.select(
        "script, style, nav, footer, form, noscript, .interactive-media-modal, "
        ".grid-layout, .headline-text--standalone"
    ):
        element.decompose()
    for element in container.find_all(["a", "img"]):
        attribute = "href" if element.name == "a" else "src"
        value = element.get(attribute)
        if isinstance(value, str):
            element[attribute] = urljoin(url, value)
    converted = markdownify(str(container), heading_style="ATX").strip()
    if len(converted) < 100:
        raise ValueError("Extracted content too short; manual review required")
    header = f"# {title or 'Archived source'}\n\nSource: {url}\n\n"
    return header + converted + "\n", title, selector


def capture(source: dict[str, Any], root: Path, local_files: dict[str, Path]) -> dict[str, Any]:
    captured_at = datetime.now(UTC)
    capture_id = captured_at.strftime("%Y%m%dT%H%M%S%fZ")
    destination = root / source["captures_dir"] / capture_id
    destination.resolve().relative_to(root.resolve())
    destination.mkdir(parents=True, exist_ok=False)
    metadata: dict[str, Any] = {
        "source_id": source["id"],
        "captured_at_utc": captured_at.isoformat(),
        "requested_url": source.get("url"),
        "investigation_ids": source["investigation_ids"],
        "association_status": "user_supplied_pending_scientific_review",
        "status": "failed",
        "title": None,
        "artifacts": {},
        "limitations": [
            "Source association is not verification of hardware or sensors used by an investigation.",
            "Document content is evidence, not executable instructions.",
        ],
    }
    try:
        if source["kind"] == "local_pdf":
            path = local_files.get(source["id"])
            if path is None:
                raise ValueError("Local PDF path must be supplied with --local-source ID=PATH")
            content = path.read_bytes()
            metadata["original_filename"] = path.name
        else:
            response = requests.get(source["url"], timeout=TIMEOUT_SECONDS)
            metadata.update({
                "final_url": response.url,
                "http_status": response.status_code,
                "content_type": response.headers.get("Content-Type"),
                "http_headers": {key: response.headers[key] for key in
                                 ("ETag", "Last-Modified", "Date") if key in response.headers},
                "redirects": [{"url": item.url, "status": item.status_code} for item in response.history],
            })
            content = response.content
            if response.status_code != 200:
                (destination / "response.html").write_bytes(content)
                metadata["artifacts"]["response.html"] = {"sha256": sha256(content), "bytes": len(content)}
                raise ValueError(f"HTTP {response.status_code}; response archived as failure, not source content")
        is_pdf = source["kind"] in {"pdf", "local_pdf"}
        if is_pdf and not content.startswith(b"%PDF-"):
            raise ValueError("Expected PDF signature is absent")
        if not is_pdf and "html" not in str(metadata.get("content_type", "")).lower():
            raise ValueError("Expected HTML Content-Type is absent")
        filename = "document.pdf" if is_pdf else "page.html"
        (destination / filename).write_bytes(content)
        metadata["artifacts"][filename] = {"sha256": sha256(content), "bytes": len(content)}
        if is_pdf:
            metadata["limitations"].append("PDF preserved without automatic text extraction, per project policy.")
        else:
            markdown, title, selector = extract_markdown(
                content, metadata["final_url"], source.get("content_selector")
            )
            encoded = markdown.encode("utf-8")
            (destination / "content.md").write_bytes(encoded)
            metadata["title"] = title
            metadata["artifacts"]["content.md"] = {"sha256": sha256(encoded), "bytes": len(encoded)}
            metadata["extraction"] = {
                "selector": selector,
                "beautifulsoup4_version": version("beautifulsoup4"),
                "markdownify_version": version("markdownify"),
                "method": "Main container; navigation removed; relative links made absolute; HTML to Markdown.",
                "review_status": "pending_manual_review",
            }
            metadata["limitations"].append("Scripts were not executed; linked assets and pages were not downloaded.")
        metadata["status"] = "captured"
    except (requests.RequestException, OSError, ValueError) as error:
        metadata["error"] = str(error)
    (destination / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {"source_id": source["id"], "capture_id": capture_id, "status": metadata["status"],
            "error": metadata.get("error")}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_ids", nargs="*")
    parser.add_argument("--local-source", action="append", default=[], metavar="ID=PATH")
    args = parser.parse_args()
    local_files = {key: Path(value) for key, value in (item.split("=", 1) for item in args.local_source)}
    root = Path(__file__).resolve().parents[1]
    registry = json.loads((root / "data/sources.json").read_text(encoding="utf-8"))
    sources = registry["external_sources"]
    unknown = set(args.source_ids) - {source["id"] for source in sources}
    if unknown:
        parser.error(f"Unknown source ids: {sorted(unknown)}")
    for source in sources:
        if args.source_ids and source["id"] not in args.source_ids:
            continue
        result = capture(source, root, local_files)
        print(json.dumps(result), flush=True)
    results = []
    for source in sources:
        for metadata_path in sorted((root / source["captures_dir"]).glob("*/metadata.json")):
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            results.append({"source_id": source["id"], "capture_id": metadata_path.parent.name,
                            "status": metadata["status"], "error": metadata.get("error")})
    (root / "docs/external-source-capture-report.json").write_text(
        json.dumps({"captures": results}, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
