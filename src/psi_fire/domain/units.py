"""Canonical units and conversions. Pure domain: no I/O."""

from dataclasses import dataclass
from enum import StrEnum

from psi_fire.domain.errors import UnknownUnitError


class Unit(StrEnum):
    PSI = "psi"
    PERCENT = "percent"
    PPM = "ppm"
    MM = "mm"
    CM_S = "cm_s"
    MM2_S = "mm2_s"
    S = "s"
    W = "w"
    MG_S = "mg_s"
    SCCM = "sccm"
    K = "k"
    DIMENSIONLESS = ""


MMHG_TO_PSI = 0.0193368
ATM_TO_PSI = 14.6959
BAR_TO_PSI = 14.5038
KPA_TO_PSI = 0.145038
FRACTION_TO_PERCENT = 100.0
CM_TO_MM = 10.0
MICRON_TO_MM = 0.001
MM_S_TO_CM_S = 0.1
MIN_TO_S = 60.0
PER_MIN_TO_PER_S = 1 / 60
CELSIUS_TO_KELVIN_OFFSET = 273.15
CANONICAL_DECIMALS = 9  # strips float noise such as 0.21 * 100 = 21.000000000000004


@dataclass(frozen=True)
class _Conversion:
    unit: Unit
    factor: float = 1.0
    offset: float = 0.0


_SOURCE_UNITS: dict[str, _Conversion] = {
    "psi": _Conversion(Unit.PSI),
    "mmhg": _Conversion(Unit.PSI, MMHG_TO_PSI),
    "atm": _Conversion(Unit.PSI, ATM_TO_PSI),
    "bar": _Conversion(Unit.PSI, BAR_TO_PSI),
    "kpa": _Conversion(Unit.PSI, KPA_TO_PSI),
    "%": _Conversion(Unit.PERCENT),
    "percent": _Conversion(Unit.PERCENT),
    "mole fraction": _Conversion(Unit.PERCENT, FRACTION_TO_PERCENT),
    "fraction": _Conversion(Unit.PERCENT, FRACTION_TO_PERCENT),
    "ppm": _Conversion(Unit.PPM),
    "mm": _Conversion(Unit.MM),
    "cm": _Conversion(Unit.MM, CM_TO_MM),
    "micron": _Conversion(Unit.MM, MICRON_TO_MM),
    "cm/s": _Conversion(Unit.CM_S),
    "mm/s": _Conversion(Unit.CM_S, MM_S_TO_CM_S),
    "mm2/s": _Conversion(Unit.MM2_S),
    "s": _Conversion(Unit.S),
    "sec": _Conversion(Unit.S),
    "min": _Conversion(Unit.S, MIN_TO_S),
    "minutes": _Conversion(Unit.S, MIN_TO_S),
    "w": _Conversion(Unit.W),
    "mg/s": _Conversion(Unit.MG_S),
    "mg/min": _Conversion(Unit.MG_S, PER_MIN_TO_PER_S),
    "sccm": _Conversion(Unit.SCCM),
    "k": _Conversion(Unit.K),
    "c": _Conversion(Unit.K, 1.0, CELSIUS_TO_KELVIN_OFFSET),
}


def _conversion(source_unit: str | None) -> _Conversion:
    if source_unit is None:
        return _Conversion(Unit.DIMENSIONLESS)
    try:
        return _SOURCE_UNITS[source_unit.strip().lower()]
    except KeyError:
        raise UnknownUnitError(f"unknown unit {source_unit!r}") from None


def canonical_unit(source_unit: str | None) -> Unit:
    return _conversion(source_unit).unit


def to_canonical(value: float, source_unit: str | None) -> float:
    conversion = _conversion(source_unit)
    return round(value * conversion.factor + conversion.offset, CANONICAL_DECIMALS)


def column_name(base: str, unit: Unit) -> str:
    """Ubiquitous column naming: the canonical unit is always part of the name."""
    return base if unit is Unit.DIMENSIONLESS else f"{base}_{unit.value}"
