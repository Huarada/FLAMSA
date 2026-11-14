"""Manually curated investigation facts. Every fact carries its evidence (file + locator + literal quote)."""

from datetime import date
from enum import StrEnum
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, model_validator

T = TypeVar("T")


class FireSafetyPillar(StrEnum):
    PREVENTION = "prevention"
    DETECTION = "detection"
    SUPPRESSION = "suppression"


class GravityRegime(StrEnum):
    MICROGRAVITY = "microgravity"
    PARTIAL_EMULATED = "partial_emulated"  # E-FIELD only: electric field mimics partial gravity
    NORMAL = "normal"


class ReviewStatus(StrEnum):
    DRAFT = "draft"        # written from the sources, not yet checked by a human
    REVIEWED = "reviewed"  # a named human compared every quote with its source


class ClaimStatus(StrEnum):
    VERIFIED = "verified"          # the source states the value explicitly
    INFERRED = "inferred"          # the curator derived it from the quoted text; the note says how
    NOT_REPORTED = "not_reported"  # searched and not found; value stays empty, never guessed


class Evidence(BaseModel):
    """Where a fact comes from. `quote` must appear literally in `source_file` (checked at curation)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source_file: str  # repo-relative path, forward slashes (clickable in the dashboard)
    locator: str      # "p. 12" (PDF page), "para 3" (DOCX paragraph) or a field/section name
    quote: str
    source_url: str | None = None  # original web location when the file is a capture


class Claim(BaseModel, Generic[T]):
    model_config = ConfigDict(frozen=True, extra="forbid")

    value: T | None
    status: ClaimStatus
    evidence: tuple[Evidence, ...] = ()
    note: str | None = None  # mandatory for inferred (how derived) and not_reported (what was searched)

    @model_validator(mode="after")
    def _check_invariants(self) -> "Claim[T]":
        if self.status is ClaimStatus.NOT_REPORTED:
            if self.value is not None:
                raise ValueError("a not_reported claim must have an empty value")
            if not self.note:
                raise ValueError("a not_reported claim must say which sources were searched")
            return self
        if self.value is None:
            raise ValueError(f"a {self.status.value} claim needs a value")
        if not self.evidence:
            raise ValueError(f"a {self.status.value} claim needs at least one piece of evidence")
        if self.status is ClaimStatus.INFERRED and not self.note:
            raise ValueError("an inferred claim must explain how it was derived")
        return self


INSTRUMENT_FORBIDDEN = ("(", ")", ",", ";", " and ", "/")


class Sensor(BaseModel):
    """`instrument` is a filter label in the dashboard: one plain instrument per claim, no counts or details."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    instrument: str  # e.g. "thermocouple", "radiometer"; counts, types, positions go in Claim.note
    measures: str | None = None  # only what the cited quote states; None = the source does not say

    @model_validator(mode="after")
    def _check_instrument_label(self) -> "Sensor":
        bad = [token for token in INSTRUMENT_FORBIDDEN if token in self.instrument]
        if bad or not self.instrument.strip():
            raise ValueError(f"instrument must be one plain label (found {bad or 'empty'}): {self.instrument!r}")
        return self


class NominalAtmosphere(BaseModel):
    """Atmosphere the investigation was designed for, when the tables do not carry it."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    o2_percent_min: float | None = None
    o2_percent_max: float | None = None
    pressure_psi_min: float | None = None
    pressure_psi_max: float | None = None

    @model_validator(mode="after")
    def _check_invariants(self) -> "NominalAtmosphere":
        for base in ("o2_percent", "pressure_psi"):
            low, high = getattr(self, f"{base}_min"), getattr(self, f"{base}_max")
            if (low is None) != (high is None) or (low is not None and low > high):
                raise ValueError(f"{base}: min/max must be set together and ordered")
        if self.o2_percent_min is None and self.pressure_psi_min is None:
            raise ValueError("a nominal atmosphere needs O2 or pressure")
        return self


class ManualMetadata(BaseModel):
    """Contents of data/manual/<investigation_id>.json."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    investigation_id: str
    review_status: ReviewStatus
    reviewed_by: str | None = None
    reviewed_on: date | None = None
    pillars: Claim[tuple[FireSafetyPillar, ...]]
    gravity_regime: Claim[GravityRegime]
    hardware: Claim[str]
    nominal_atmosphere: Claim[NominalAtmosphere] | None = None  # None: the tables carry O2/pressure per test
    sensors: tuple[Claim[Sensor], ...]
    earth_applications: tuple[Claim[str], ...] = ()

    @model_validator(mode="after")
    def _check_invariants(self) -> "ManualMetadata":
        if self.review_status is ReviewStatus.REVIEWED and not (self.reviewed_by and self.reviewed_on):
            raise ValueError("a reviewed file must name its reviewer and date")
        return self

    def all_evidence(self) -> list[Evidence]:
        claims: list[Claim] = [  # type: ignore[type-arg]
            self.pillars, self.gravity_regime, self.hardware, *self.sensors, *self.earth_applications,
            *([self.nominal_atmosphere] if self.nominal_atmosphere else []),
        ]
        return [e for claim in claims for e in claim.evidence]
