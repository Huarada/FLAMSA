"""Inventory structured sources without modifying or curating raw scientific data."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any
from zipfile import BadZipFile, ZipFile

STRUCTURED_SUFFIXES = {".csv", ".txt", ".xlsx", ".xls"}
INSTRUMENT_PATTERN = re.compile(
    r"camera|radiometer|thermocouple|anemometer|smoke detector|"
    r"heat flux sensor|solid state sensor|thermophoretic|electron microscope|"
    r"p-trak|dusttrak|sensor|pyromet|photograph",
    re.IGNORECASE,
)
HARDWARE_PATTERN = re.compile(
    r"glovebox|glove box|combustion integrated rack|\bMDCA\b|"
    r"droplet combustion appar|experiment hardware|enclosure in Cygnus",
    re.IGNORECASE,
)
PROVENANCE_HEADERS = {"source_file", "source_row", "provenance_status"}
EXAMPLE_LIMIT = 12
SHEET_NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def raw_snapshot(directories: list[Path]) -> dict[Path, str]:
    return {
        path: digest(path)
        for directory in directories
        for path in directory.rglob("*")
        if path.is_file()
    }


def read_text(path: Path) -> tuple[str, str]:
    raw = path.read_bytes()
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return raw.decode("utf-16"), "utf-16"
    try:
        return raw.decode("utf-8-sig"), "utf-8-sig"
    except UnicodeDecodeError:
        return raw.decode("cp1252"), "cp1252"


def source_ref(investigation_id: str, filename: str) -> dict[str, str]:
    return {"investigation_id": investigation_id, "relative_file": filename}


def evidence_hits(text: str) -> dict[str, object]:
    hardware = []
    instruments = []
    for number, line in enumerate(text.splitlines(), 1):
        item = {"line": number, "raw": line}
        if HARDWARE_PATTERN.search(line):
            hardware.append(item)
        if INSTRUMENT_PATTERN.search(line):
            instruments.append(item)
    return {
        "hardware_match_count": len(hardware),
        "hardware_examples": hardware[:EXAMPLE_LIMIT],
        "instrument_match_count": len(instruments),
        "instrument_examples": instruments[:EXAMPLE_LIMIT],
    }


def csv_inventory(text: str) -> dict[str, object]:
    reader = csv.reader(io.StringIO(text, newline=""))
    rows = []
    previous = 0
    for row in reader:
        rows.append((previous + 1, reader.line_num, row))
        previous = reader.line_num
    if not rows:
        return {"headers": [], "data_record_count": 0}
    headers = rows[0][2]
    instrument_columns = []
    for index, header in enumerate(headers):
        if not INSTRUMENT_PATTERN.search(header):
            continue
        examples = [
            {"line_start": start, "line_end": end, "raw": row[index]}
            for start, end, row in rows[1:]
            if index < len(row) and row[index].strip()
        ]
        instrument_columns.append(
            {"header_raw": header, "column": index + 1, "examples": examples[:3]}
        )
    return {
        "headers": headers,
        "data_record_count": len(rows) - 1,
        "blank_record_count": sum(not any(cell.strip() for cell in row) for _, _, row in rows[1:]),
        "nonmatching_width_record_count": sum(len(row) != len(headers) for _, _, row in rows[1:]),
        "instrument_columns": instrument_columns,
        "explicit_hardware_columns": [h for h in headers if "hardware" in h.lower()],
        "provenance_columns_present": sorted(PROVENANCE_HEADERS.intersection(headers)),
        "warning": "Records may be summaries, notes, or ranges; this is not a TestPoint count.",
    }


def isa_fields(text: str) -> list[dict[str, object]]:
    reader = csv.reader(io.StringIO(text, newline=""), delimiter="\t")
    fields: list[dict[str, object]] = []
    previous = 0
    wanted = {"Comment[Experiment Hardware]", "Comment[Approach]"}
    for row in reader:
        if row and row[0] in wanted:
            fields.append(
                {
                    "field": row[0],
                    "raw": row[1] if len(row) > 1 else None,
                    "line_start": previous + 1,
                    "line_end": reader.line_num,
                    "column": 2,
                    "status": "verified" if len(row) > 1 and row[1].strip() else "missing",
                }
            )
        previous = reader.line_num
    return fields


def spreadsheet_inventory(path: Path) -> dict[str, object]:
    with ZipFile(path) as archive:
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            strings = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = ["".join(item.itertext()) for item in strings]
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        sheets = [dict(node.attrib) for node in workbook.findall("s:sheets/s:sheet", SHEET_NS)]
        matches: list[dict[str, object]] = []
        count = 0
        for name in sorted(archive.namelist()):
            if not re.fullmatch(r"xl/worksheets/sheet\d+\.xml", name):
                continue
            sheet = ET.fromstring(archive.read(name))
            for cell in sheet.findall(".//s:c", SHEET_NS):
                value = cell.findtext("s:v", default="", namespaces=SHEET_NS)
                if cell.get("t") == "s" and value:
                    value = shared[int(value)]
                elif cell.get("t") == "inlineStr":
                    inline = cell.find("s:is", SHEET_NS)
                    value = "".join(inline.itertext()) if inline is not None else ""
                if INSTRUMENT_PATTERN.search(value) or HARDWARE_PATTERN.search(value):
                    count += 1
                    if len(matches) < EXAMPLE_LIMIT:
                        matches.append({"sheet_xml": name, "cell": cell.get("r"), "raw": value})
        return {"sheets": sheets, "keyword_cell_count": count, "keyword_examples": matches}


def run(root: Path) -> None:
    registry = json.loads((root / "data/sources.json").read_text(encoding="utf-8"))
    raw_directories = [root / item["raw_dir"] for item in registry["investigations"]]
    raw_before = raw_snapshot(raw_directories)
    investigations: list[dict[str, Any]] = []
    coverage = []
    for investigation in registry["investigations"]:
        investigation_id = investigation["id"]
        base = root / investigation["raw_dir"]
        files = []
        declared_hardware = []
        approaches = []
        instrument_tables = []
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in STRUCTURED_SUFFIXES:
                continue
            relative = path.relative_to(base).as_posix()
            item: dict[str, Any] = {
                "source_ref": source_ref(investigation_id, relative), "sha256": digest(path)
            }
            try:
                if path.suffix.lower() in {".csv", ".txt"}:
                    text, encoding = read_text(path)
                    item.update({"encoding": encoding, "scan": evidence_hits(text)})
                    if path.suffix.lower() == ".csv":
                        inventory = csv_inventory(text)
                        item["csv"] = inventory
                        if inventory.get("instrument_columns"):
                            instrument_tables.append(relative)
                    if path.name == "i_Investigation.txt":
                        fields = isa_fields(text)
                        item["isa_fields"] = fields
                        registered = investigation["isa_tab_dir"] is not None and path.parent == base / investigation["isa_tab_dir"]
                        if registered:
                            for field in fields:
                                evidence = {"source_ref": item["source_ref"], **field}
                                if field["field"] == "Comment[Experiment Hardware]":
                                    declared_hardware.append(evidence)
                                elif INSTRUMENT_PATTERN.search(str(field["raw"])):
                                    approaches.append(evidence)
                elif path.suffix.lower() == ".xlsx":
                    item["xlsx"] = spreadsheet_inventory(path)
                else:
                    item["not_reviewed"] = "Legacy XLS contents require an XLS reader; file inventoried and hashed only."
            except (UnicodeError, csv.Error, OSError, BadZipFile, ET.ParseError, IndexError, ValueError) as error:
                item["review_error"] = str(error)
            files.append(item)
        curated = root / "data/curated" / investigation_id
        metadata_exists = (curated / "investigation.json").is_file()
        csv_exists = (curated / "test_points.csv").is_file()
        summary = {
            "investigation_id": investigation_id,
            "experimental_tables": len(investigation["experimental_tables"]),
            "structured_files": len(files),
            "registered_isa_tab": bool(investigation["isa_tab_dir"]),
            "hardware_declaration_found": bool(declared_hardware),
            "instrument_mentions_in_registered_approach": bool(approaches),
            "instrument_columns_in_csv": bool(instrument_tables),
            "curated_metadata_exists": metadata_exists,
            "curated_test_points_exist": csv_exists,
            "manual_metadata_exists": (root / "data/manual" / f"{investigation_id}.json").is_file(),
        }
        coverage.append(summary)
        investigations.append(
            {"coverage": summary, "hardware_evidence": declared_hardware,
             "instrument_approach_evidence": approaches,
             "instrument_csv_sources": instrument_tables, "files": files}
        )
    raw_after = raw_snapshot(raw_directories)
    if raw_before != raw_after:
        raise RuntimeError("Raw files changed while auditing; audit cannot assert immutability.")
    all_files = [item for investigation in investigations for item in investigation["files"]]
    report = {
        "source_registry": "data/sources.json",
        "source_ref_resolution": "Join source_ref.investigation_id to registry id; append relative_file to raw_dir.",
        "scope": "All CSV, TXT, XLSX and XLS files under registered investigation directories.",
        "limitations": [
            "Evidence candidates are not curated Sensor or Hardware entities and do not prove completeness.",
            "Keyword matches can describe proposed, ground-based or post-flight instruments; review context before use.",
            "A measurement or calibration column does not establish a sensor model or deployed instrument.",
            "Hardware facility declarations do not automatically verify a specific duct or apparatus configuration.",
            "Legacy XLS files are inventoried only; PDFs, DOC/DOCX, PPT/PPTX and PXP contents were not reviewed.",
            "No normalization, TestPoint expansion, scientific validation or application tests were performed.",
        ],
        "raw_files_unchanged": True,
        "raw_files_hashed": len(raw_before),
        "structured_file_counts": dict(sorted(Counter(Path(item["source_ref"]["relative_file"]).suffix.lower() for item in all_files).items())),
        "investigations": investigations,
    }
    output = root / "docs"
    (output / "structured-data-audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (output / "structured-data-coverage.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(coverage[0]))
        writer.writeheader()
        writer.writerows(coverage)
    print(json.dumps({"investigations": len(coverage), "structured_files": report["structured_file_counts"],
                      "hardware_declarations": sum(row["hardware_declaration_found"] for row in coverage),
                      "approach_instrument_mentions": sum(row["instrument_mentions_in_registered_approach"] for row in coverage),
                      "csv_instrument_columns": sum(row["instrument_columns_in_csv"] for row in coverage),
                      "review_errors": sum("review_error" in item for item in all_files),
                      "raw_files_unchanged": True}, indent=2))


if __name__ == "__main__":
    run(Path(__file__).resolve().parents[1])
