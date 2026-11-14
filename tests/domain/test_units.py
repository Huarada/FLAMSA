import pytest

from psi_fire.domain.errors import UnknownUnitError
from psi_fire.domain.units import Unit, canonical_unit, column_name, to_canonical


@pytest.mark.parametrize(
    ("value", "unit", "expected"),
    [
        (760.0, "mmHg", 14.6959680),
        (1.0, "atm", 14.6959),
        (0.21, "mole fraction", 21.0),
        (0.33, "cm", 3.3),
        (2.1, "mm/s", 0.21),
        (25.0, "C", 298.15),
        (2.0, "mg/min", 0.033333333),
    ],
)
def test_to_canonical(value: float, unit: str, expected: float) -> None:
    assert to_canonical(value, unit) == pytest.approx(expected)


def test_dimensionless_and_naming() -> None:
    assert canonical_unit(None) is Unit.DIMENSIONLESS
    assert column_name("zst", Unit.DIMENSIONLESS) == "zst"
    assert column_name("pressure", canonical_unit("bar")) == "pressure_psi"


def test_unknown_unit_is_a_domain_error() -> None:
    with pytest.raises(UnknownUnitError):
        canonical_unit("furlongs")
