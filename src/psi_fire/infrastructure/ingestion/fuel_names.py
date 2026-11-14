"""Fuel label normalization: raw PSI fuel labels -> lower-case material, geometry and printed percentage.

Only what the label literally says is extracted. A label that names no material (for example
"1/4 clear rod") yields no material: the material is never guessed. The raw label is kept by the pipeline.
"""

import re
from dataclasses import dataclass

LABEL_FRACTION_COLUMN = "fuel_label_fraction_percent"
PURE_LABEL_PERCENT = 100.0

# Ordered specific -> generic: a matched span is consumed so "methane" is not also read as "ethane".
_MATERIALS: tuple[tuple[str, str], ...] = (
    (r"japan\s+wax", "japan wax"),
    (r"parr?aff?in(?:\s+wax)?", "paraffin wax"),  # "parrafin" is a source typo
    (r"\bwax\b", "wax"),
    (r"sibal", "sibal"),
    (r"nomex", "nomex"),
    (r"ultem", "ultem"),
    (r"pmma", "pmma"),
    (r"teflon", "teflon"),
    (r"kapton", "kapton"),
    (r"silicone\s+rubber", "silicone rubber"),
    (r"silicone", "silicone"),
    (r"lampwick", "lampwick"),
    (r"pyrell", "pyrell"),
    (r"dibutyl\s+phthalate", "dibutyl phthalate"),
    (r"methanol", "methanol"),
    (r"ethanol", "ethanol"),
    (r"propanol", "propanol"),
    (r"glycerol", "glycerol"),
    (r"iso-?dodecane", "iso-dodecane"),
    (r"c12h26", "n-dodecane"),  # the CFI objective names n-dodecane and n-dodecane/iso-dodecane mixtures
    (r"iso-?octane", "iso-octane"),
    (r"n-octane", "n-octane"),
    (r"heptane", "heptane"),
    (r"decane", "decane"),
    (r"methane|\bch4\b", "methane"),
    (r"ethane|\bc2h6\b", "ethane"),
    (r"ethylene|\bc2h4\b", "ethylene"),
    (r"propylene", "propylene"),
    (r"propane", "propane"),
    (r"butane", "butane"),
)
_GEOMETRIES: tuple[tuple[str, str], ...] = (
    (r"spher", "sphere"), (r"\brod\b", "rod"), (r"\bslab\b", "slab"), (r"\bfilm\b", "film"),
    (r"\bsheet\b", "sheet"), (r"\bcandle\b", "candle"), (r"\bfabric\b", "fabric"),
)
_LEADING_PERCENT = re.compile(r"^(\d+(?:\.\d+)?)\s*%")
_PURE = re.compile(r"\(pure\)")


@dataclass(frozen=True)
class FuelLabel:
    name: str | None
    geometry: str | None
    label_fraction_percent: float | None


def _materials(text: str) -> list[str]:
    found: list[tuple[int, str]] = []
    for pattern, name in _MATERIALS:
        for match in re.finditer(pattern, text):
            found.append((match.start(), name))
            text = text[:match.start()] + " " * (match.end() - match.start()) + text[match.end():]
    return list(dict.fromkeys(name for _, name in sorted(found)))


def normalize_fuel_label(raw: str) -> FuelLabel:
    text = " ".join(raw.lower().split())
    names = _materials(text)
    geometry = next((name for pattern, name in _GEOMETRIES if re.search(pattern, text)), None)
    fraction = None
    if percent := _LEADING_PERCENT.match(text):
        fraction = float(percent[1])
    elif _PURE.search(text):
        fraction = PURE_LABEL_PERCENT
    return FuelLabel("+".join(names) or None, geometry, fraction)
