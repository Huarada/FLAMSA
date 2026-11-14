"""Reads the STUDY section of an ISA-Tab i_Investigation.txt into flat snake_case metadata."""

import csv
import io
import re
from pathlib import Path

from psi_fire.infrastructure.ingestion.text_source import decode


def _key(raw_key: str) -> str:
    inner = re.fullmatch(r"Comment\[(.*)\]", raw_key)
    return re.sub(r"[^a-z0-9]+", "_", (inner[1] if inner else raw_key).lower()).strip("_")


def read_study_metadata(path: Path) -> dict[str, str]:
    text, _ = decode(path.read_bytes())
    metadata: dict[str, str] = {}
    in_study = False
    for row in csv.reader(io.StringIO(text, newline=""), delimiter="\t"):
        if not row or not row[0].strip():
            continue
        key = row[0].strip()
        if len(row) == 1 and key.isupper():  # section header such as "STUDY" or "STUDY DESIGN DESCRIPTORS"
            in_study = key == "STUDY"
            continue
        value = " ".join(" ".join(cell.split()) for cell in row[1:] if cell.strip())
        if in_study and value:
            metadata[_key(key)] = value
    return metadata
