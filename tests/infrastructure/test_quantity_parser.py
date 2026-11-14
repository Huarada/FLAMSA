import pytest

from psi_fire.domain.units import Unit
from psi_fire.infrastructure.ingestion.quantity_parser import (
    QuantityParseError,
    format_number,
    parse_quantity,
)


@pytest.mark.parametrize(
    ("raw", "default_unit", "expected"),
    [
        ("~ 21.5", "%", (21.5, 21.5)),
        ("21.5 - 21.7", "%", (21.5, 21.7)),
        ("22.1 to 22.0", "%", (22.0, 22.1)),
        ("0.17; 0.21;0.25; 0.3", "mole fraction", (17.0, 30.0)),
        ("0.5; 1.0; 1.5; 2.0; or 3.0", "atm", (7.34795, 44.0877)),
        ("30 cm/s", "cm/s", (30.0, 30.0)),
        (".33 cm", "cm", (3.3, 3.3)),
        ("1 cm", "mm", (10.0, 10.0)),
        ("-1", "ppm", (-1.0, -1.0)),
        ("~ 10 cm (note 3)", "cm", (100.0, 100.0)),
    ],
)
def test_parses_real_cell_formats(raw: str, default_unit: str, expected: tuple[float, float]) -> None:
    quantity = parse_quantity(raw, default_unit)
    assert quantity is not None
    assert (quantity.minimum, quantity.maximum) == pytest.approx(expected)


@pytest.mark.parametrize("raw", ["", "  ", "none", "n/a", "n/a (Nomex)", "-"])
def test_empty_cells_are_none(raw: str) -> None:
    assert parse_quantity(raw, "s") is None


@pytest.mark.parametrize(
    "raw",
    ["Insignificant", "See Fig. 5", "037 mm", "2.1 mm/s"],  # text, ambiguous leading zero, wrong dimension
)
def test_unreadable_cells_raise(raw: str) -> None:
    with pytest.raises(QuantityParseError):
        parse_quantity(raw, "mm")


def test_unit_in_value_overrides_header_unit() -> None:
    quantity = parse_quantity("1.2 mm/s", "cm/s")
    assert quantity is not None and quantity.unit is Unit.CM_S and quantity.minimum == pytest.approx(0.12)


def test_format_number_round_trips() -> None:
    for value in (21.0, 13.697324903, 0.033333333, 1e-05):
        assert float(format_number(value)) == value
    assert format_number(21.0) == "21"
