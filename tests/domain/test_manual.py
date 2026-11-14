import pytest
from pydantic import ValidationError

from psi_fire.domain.manual import Claim, ClaimStatus, Evidence, ManualMetadata, NominalAtmosphere, Sensor

EVIDENCE = Evidence(source_file="knowledgeBase/x.txt", locator="p. 1", quote="a literal quote from the source")


def test_verified_claim_needs_value_and_evidence() -> None:
    with pytest.raises(ValidationError, match="evidence"):
        Claim[str](value="x", status=ClaimStatus.VERIFIED)
    with pytest.raises(ValidationError, match="value"):
        Claim[str](value=None, status=ClaimStatus.VERIFIED, evidence=(EVIDENCE,))


def test_inferred_claim_must_explain_itself() -> None:
    with pytest.raises(ValidationError, match="explain"):
        Claim[str](value="x", status=ClaimStatus.INFERRED, evidence=(EVIDENCE,))
    assert Claim[str](value="x", status=ClaimStatus.INFERRED, evidence=(EVIDENCE,), note="derived from the quote")


def test_not_reported_claim_is_empty_and_says_what_was_searched() -> None:
    with pytest.raises(ValidationError, match="empty"):
        Claim[str](value="21", status=ClaimStatus.NOT_REPORTED, note="searched")
    with pytest.raises(ValidationError, match="searched"):
        Claim[str](value=None, status=ClaimStatus.NOT_REPORTED)


def test_nominal_atmosphere_ranges_are_ordered_and_complete() -> None:
    with pytest.raises(ValidationError):
        NominalAtmosphere(o2_percent_min=30.0)
    with pytest.raises(ValidationError):
        NominalAtmosphere(pressure_psi_min=15.0, pressure_psi_max=10.0)
    with pytest.raises(ValidationError):
        NominalAtmosphere()


def test_reviewed_file_names_its_reviewer() -> None:
    claim = Claim[str](value="x", status=ClaimStatus.VERIFIED, evidence=(EVIDENCE,))
    empty = Claim[NominalAtmosphere](value=None, status=ClaimStatus.NOT_REPORTED, note="searched")
    base = {
        "investigation_id": "X", "pillars": {"value": ["prevention"], "status": "verified", "evidence": [EVIDENCE]},
        "gravity_regime": {"value": "microgravity", "status": "verified", "evidence": [EVIDENCE]},
        "hardware": claim, "nominal_atmosphere": empty, "sensors": [],
    }
    assert ManualMetadata.model_validate(base | {"review_status": "draft"})
    with pytest.raises(ValidationError, match="reviewer"):
        ManualMetadata.model_validate(base | {"review_status": "reviewed"})


@pytest.mark.parametrize(
    "label",
    ["thermocouples (2)", "intensified video camera and color camera", "thermocouple, radiometer", "CO/CO2 sensor", " "],
)
def test_instrument_must_be_one_plain_filter_label(label: str) -> None:
    with pytest.raises(ValidationError, match="plain label"):
        Sensor(instrument=label)


def test_sensor_measures_is_optional() -> None:
    assert Sensor(instrument="thermocouple").measures is None
    assert Sensor(instrument="anemometer", measures="flow velocity").measures == "flow velocity"
