"""Parses raw PSI cell strings ("~ 21.5", "21.5 - 21.7", "0.17; 0.21", "30 cm/s") into canonical ranges."""

import re
from dataclasses import dataclass

from psi_fire.domain.errors import UnknownUnitError
from psi_fire.domain.units import Unit, canonical_unit, to_canonical

EMPTY_TOKENS = frozenset({"", "none", "n/a", "na", "-", "--", "?"})

_NUMBER = r"-?(?:\d+(?:\.\d*)?|\.\d+)"
_PART = re.compile(rf"^~?\s*(?P<number>{_NUMBER})\s*(?P<unit>[A-Za-z%][A-Za-z%/0-9]*)?$")
# list separators (";", "or", "to", "and", "&") and ranges ("1.5 - 5"), never a leading minus sign
_SEPARATOR = re.compile(r"\s*(?:;|\bor\b|\bto\b|\band\b|&)\s*|(?<=[\d.%a-zA-Z])\s+-\s+")
_PARENTHETICAL = re.compile(r"\([^)]*\)")
_LEADING_ZERO_INTEGER = re.compile(r"^-?0\d")  # "037 mm" is ambiguous (0.37? 37?): never guess


class QuantityParseError(ValueError):
    """The cell is not empty but cannot be read as a quantity; the raw text must be kept."""


@dataclass(frozen=True)
class ParsedQuantity:
    minimum: float
    maximum: float
    unit: Unit
    part_count: int


def is_empty(raw: str) -> bool:
    return raw.strip().lower() in EMPTY_TOKENS


def format_number(value: float) -> str:
    """Shortest exact round-trip representation; integers lose the trailing '.0'."""
    return repr(float(value)).removesuffix(".0")


def parse_quantity(raw: str, default_unit: str | None) -> ParsedQuantity | None:
    """Returns None for empty cells; raises QuantityParseError for text that is not a quantity."""
    text = _PARENTHETICAL.sub("", raw).strip()
    if is_empty(text):
        return None
    parts = [p for p in _SEPARATOR.split(text) if p]
    matches = [_PART.match(p.strip()) for p in parts]
    if not all(matches):
        raise QuantityParseError(f"not a quantity: {raw!r}")

    explicit_units = [m["unit"] for m in matches if m and m["unit"]]
    source_unit = explicit_units[0] if explicit_units else default_unit
    try:
        expected = canonical_unit(default_unit)
        units = {canonical_unit(u) for u in [source_unit, *explicit_units]}
    except UnknownUnitError as error:
        raise QuantityParseError(str(error)) from None
    if units != {expected}:
        raise QuantityParseError(f"unit mismatch in {raw!r}: expected {expected.value or 'dimensionless'}")

    values = []
    for match in matches:
        assert match is not None
        number = match["number"]
        if _LEADING_ZERO_INTEGER.match(number):
            raise QuantityParseError(f"ambiguous leading zero in {raw!r}")
        values.append(to_canonical(float(number), source_unit))
    return ParsedQuantity(min(values), max(values), expected, len(values))
