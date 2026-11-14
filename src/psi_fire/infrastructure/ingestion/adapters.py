"""One adapter per investigation: aliases and quirks only. Shared logic lives in pipeline.py.

Headers are written whitespace-normalized; the pipeline normalizes raw headers the same way.
Every raw header must be mapped (Num/Text/Meta) or explicitly skipped, or curation fails.
"""

import re
from collections.abc import Mapping

from psi_fire.domain.model import FuelPhase, RecordLevel
from psi_fire.infrastructure.ingestion.specs import AdapterSpec, Constant, Meta, Num, Skip, TableSpec, Text

AMBIENT_O2 = {"o2_basis": Constant("ambient", "O2 column reports the chamber atmosphere")}

# Physical-consistency thresholds (docs/DATA_QUALITY_REVIEW.md, ADR-0080)
SPICE_75_PROPYLENE_MIN_DENSITY = 1.0  # kg/m3; 75/25 C3H6/N2 is ~1.57, methane (the wrong value seen) 0.65
BASS_II_MAX_BURN_O2_DROP = 10.0  # points; ~17 g PMMA in the 250 L work volume, above any burn in the report
BASS_II_O2_RISE_TOLERANCE = 0.5  # points; nothing in the glovebox adds O2, observed sensor jitter is 0.1
COMPOSITION_TOLERANCE = 0.005  # mole fraction; rounding of two-decimal cells


def _number(text: str) -> float | None:
    try:
        return float(text)
    except ValueError:
        return None


def excel_percent_artifact(raw: str, _row: Mapping[str, str]) -> tuple[str, str] | None:
    """'3400%' is 34 rendered with Excel percent formatting; neighbouring rows list 21-40 percent."""
    match = re.fullmatch(r"(\d+)00%", raw.strip())
    if match and int(match[1]) <= 100:
        return match[1], f"read {raw!r} as {match[1]} percent (Excel percent-format artifact)"
    return None


def negative_reading_as_missing(raw: str, _row: Mapping[str, str]) -> tuple[str, str] | None:
    """A negative speed or concentration is a sensor zero offset, not a physical value: drop it, keep raw."""
    if raw.strip().startswith("-"):
        return "", f"negative reading {raw!r} treated as missing (sensor offset near zero)"
    return None


def zero_pressure_as_missing(raw: str, _row: Mapping[str, str]) -> tuple[str, str] | None:
    """A burning droplet cannot sit at 0 mmHg (FLEX test 114): the cell is a source defect, not a pressure."""
    if raw.strip() in {"0", "0.0"}:
        return "", f"{raw!r} mmHg treated as missing (physically impossible for a burning droplet)"
    return None


def zero_extinction_on_disruption(raw: str, row: Mapping[str, str]) -> tuple[str, str] | None:
    """0 mm means burned to completion; a disrupted droplet broke up before any extinction diameter."""
    if raw.strip() in {"0", "0.0"} and row["Test end"].strip().lower() == "disruption":
        return "", "0 mm on a disruption outcome treated as missing (no extinction diameter was measurable)"
    return None


def spice_mass_flow_density_mismatch(raw: str, row: Mapping[str, str]) -> tuple[str, str] | None:
    """mg/s = sccm x density; for '75 % Propylene' some rows used methane's density (review 2.1)."""
    mass, volume = _number(row["Fuel Rate (mg/s)"]), _number(row["Fuel Rate (sccm)"])
    if not row["Fuel"].lower().startswith("75 % propylene") or not mass or not volume:
        return None
    density = mass * 60 / volume
    if density < SPICE_75_PROPYLENE_MIN_DENSITY:
        return "", (f"treated as missing: implied density {density:.3f} kg/m3 contradicts 75% propylene in N2 "
                    "(~1.57 kg/m3, SPICE Final Report p. 9)")
    return None


def bass_ii_impossible_final_o2(raw: str, row: Mapping[str, str]) -> tuple[str, str] | None:
    """Burns lower O2 by tenths to ~3 points (Summary Report p. 14); a rise or a collapse is a logging defect."""
    final, initial = _number(raw), _number(row["Calibrated initial O2 % by vol"])
    if final is None or initial is None:
        return None
    if final > initial + BASS_II_O2_RISE_TOLERANCE or initial - final > BASS_II_MAX_BURN_O2_DROP:
        return "", f"{raw}% treated as missing: impossible change from {initial}% in the 250 L work volume"
    return None


def ignition_conflict(raw: str, row: Mapping[str, str]) -> tuple[str, str] | None:
    """Keep the reported burn time, but flag it when the same row says there was no hot ignition."""
    burn = _number(raw)
    if burn and row["Hot ignition"].strip().lower() == "no":
        return raw, f"kept as reported; conflicts with 'Hot ignition = No' (comment: {row['Comments']!r})"
    return None


def composition_not_closed(raw: str, row: Mapping[str, str]) -> tuple[str, str] | None:
    """Mole fractions must sum to 1; the missing share cannot be assigned to any species, so only flag."""
    parts = [_number(row[h]) for h in ("Oxygen", "Nitrogen", "Helium")]
    if None not in parts and abs(sum(p for p in parts if p is not None) - 1) > COMPOSITION_TOLERANCE:
        return raw, f"kept as reported; O2 + N2 + He = {sum(p for p in parts if p is not None):.2f}, not 1"
    return None


def _saffire_note_row(cells: list[str]) -> bool:
    first = cells[0].strip()
    return first.startswith("Note") or bool(re.match(r"^F\d+C\d", first))  # footnotes, flow-visualization videos


_SAFFIRE_CAMERAS = (Meta("Camera 1", "camera_1_video"), Meta("Camera 2", "camera_2_video"))

_CFI_G_SHARED = (
    Text("Flame Type", "flame_configuration"),
    Meta("Day", "campaign_day"),
    Text("Fuel", "fuel_name"),
    Meta("Test", "test_point_id"),
    Num("approx p (bar)", "pressure", "bar"),
    Text("TFP", "tfp"),
    Num("Tad (K)", "adiabatic_flame_temperature", "K"),
    Num("Zst", "stoichiometric_mixture_fraction", None),
    Text("Hot ignition", "hot_ignition"),
    Num("burn time (sec)", "burn_time", "sec", fixup=ignition_conflict),
    Text("Comments", "comments", free_text=True),
)

ADAPTERS: dict[str, AdapterSpec] = {
    a.investigation_id: a
    for a in (
        AdapterSpec(
            "BASS", RecordLevel.TEST, FuelPhase.SOLID,
            (TableSpec("PSI-26_Experimental table_BASS.csv", (
                Meta("Date", "test_date"),
                Meta("GMT", "gmt_day_of_year"),
                Meta("As Run Test #", "as_run_test_number"),  # not unique in the source: ids are row-based
                Meta("Test #", "planned_test_number"),
                Meta("Sample #", "sample_number"),
                Text("Fuel Sample Material", "fuel_name"),
            )),),
        ),
        AdapterSpec(
            "BASS-II", RecordLevel.TEST, FuelPhase.SOLID,
            (TableSpec("PSI-25_Experimental table_BASS-II.csv", (
                Meta("PI", "principal_investigator"),
                Meta("Test #", "test_point_id"),
                Meta("Date", "test_date"),
                Meta("GMT", "gmt_day_of_year"),
                Meta("Sample #", "sample_number"),
                Text("Fuel Sample Material", "fuel_name"),
                Text("Flow restrictor", "flow_restrictor_setting"),
                Text("Fan display", "fan_display_setting"),
                Text("Air display", "air_display_setting"),
                Meta("Radiometer gain (1000 250 50 10)", "radiometer_gain"),
                Meta("Total Frames Shot", "total_frames_shot"),
                Num("Calibrated initial O2 % by vol", "o2", "%"),
                Num("Calibrated final O2 % by vol", "o2_final", "%", fixup=bass_ii_impossible_final_o2),
                Num("Initial CO2 % by vol", "co2_initial", "%"),
                Num("Final CO2 % by vol", "co2_final", "%"),
                Num("Initial CO (ppm)", "co_initial", "ppm", fixup=negative_reading_as_missing),
                Num("Final CO (ppm)", "co_final", "ppm", fixup=negative_reading_as_missing),
            ), AMBIENT_O2),),
        ),
        AdapterSpec(
            "SAFFIRE-I", RecordLevel.TEST, FuelPhase.SOLID,
            (TableSpec("PSI-98_Experimental table_SAFFIRE-1.csv", (
                Meta("Sample Number", "test_point_id"),
                Text("Material", "fuel_name"),
                Num("Sample Thickness (cm)", "sample_thickness", "cm"),
                Num("Sample Length (cm)", "sample_length", "cm"),
                Num("Sample Width (cm)", "sample_width", "cm"),
                Num("Air Flow (cm/s)", "flow_speed", "cm/s"),
                Num("Percent O2", "o2", "%"),
                Num("Ignition Power (W)", "ignition_power", "W"),
                Num("Ignition Time (s)", "ignition_time", "s"),
                Num("Burn Time (s)", "burn_time", "s"),
                Text("Flow Direction", "flow_direction"),
                *_SAFFIRE_CAMERAS,
            ), AMBIENT_O2),),
            is_note_row=_saffire_note_row,
        ),
        AdapterSpec(
            "SAFFIRE-II", RecordLevel.TEST, FuelPhase.SOLID,
            (TableSpec("PSI-99_Experimental table_SAFFIRE-2.csv", (
                Meta("Sample Number", "test_point_id"),
                Text("Material", "fuel_name"),
                Num("Samle Thickness", "sample_thickness", "mm"),
                Num("Sample Length", "sample_length", "cm"),
                Num("Sample Width (cm)", "sample_width", "cm"),
                Num("Air Flow (cm/s)", "flow_speed", "cm/s"),
                Num("Percent O2 (Note 1)", "o2", "%"),
                Num("Ignition Power (W)", "ignition_power", "W"),
                Num("Ignition Time (s)", "ignition_time", "s"),
                Num("Burn Time (s)", "burn_time", "s"),
                Text("Flow Direction", "flow_direction"),
                # "?" is a lost "µ" (micro-gravity); the "Spread Length" column holds rates in mm/s
                Num("?-g Burn Length", "microgravity_burn_length", "cm"),
                Num("?-g Spread Length", "microgravity_spread_rate", "mm/s"),
                Num("1-g Burn Length", "normal_gravity_burn_length", "cm"),
                Num("1-g Spread Rate", "normal_gravity_spread_rate", "mm/s"),
                *_SAFFIRE_CAMERAS,
            ), AMBIENT_O2),),
            is_note_row=_saffire_note_row,
        ),
        AdapterSpec(
            "SAFFIRE-III", RecordLevel.TEST, FuelPhase.SOLID,
            (TableSpec("PSI-100_Experimental table_SAFFIRE-3.csv", (
                Meta("Sample Number", "test_point_id"),
                Text("Material", "fuel_name"),
                Num("Sample Thickness", "sample_thickness", "cm"),
                Num("Sample Length", "sample_length", "cm"),
                Num("Sample Width", "sample_width", "cm"),
                Num("Air Flow", "flow_speed", "cm/s"),
                Text("Direction", "flow_direction"),
                *_SAFFIRE_CAMERAS,
            )),),
        ),
        AdapterSpec(
            "SAME", RecordLevel.TEST, FuelPhase.SOLID,
            (TableSpec("PSI-102_Experimental table_SAME.csv", (
                Meta("Sample #", "test_point_id"),
                Text("Sample Material", "fuel_name"),
                Num("Air Flow (cm/s)", "flow_speed", "cm/s"),
                Num("Weight loss rate (mg/min)", "sample_mass_loss_rate", "mg/min"),
                Num("Aging Duration (minutes)", "smoke_aging_duration", "minutes"),
            )),),
            fuel_phase_overrides={"dibutyl phthalate": FuelPhase.LIQUID},
        ),
        AdapterSpec(
            "SAME-R", RecordLevel.TEST, FuelPhase.SOLID,
            (TableSpec("PSI-101_Experimental table_SAME-R.csv", (
                Text("Sample Type", "fuel_name"),
                Meta("SAME Test #", "same_test_number"),  # reused across samples (57): ids are row-based
                Text("Description", "test_description", free_text=True),
                Meta("Date", "test_date"),
                Num("Inlet velocity (cm/s)", "flow_speed", "cm/s"),
                Num("Rt/R0", "rt_r0_ratio", None),
                Num("Duration (sec)", "smoke_generation_duration", "sec"),
                Num("Primary aging time (sec)", "primary_aging_time", "sec"),
                Num("Primary mixing time (sec)", "primary_mixing_time", "sec"),
                Num("Net aging time (sec)", "net_aging_time", "sec"),
            )),),
            # the SAME-R final report calls the same samples "silicone rubber" (p. 3-4); ADR-0062
            fuel_aliases={"silicone": "silicone rubber"},
        ),
        AdapterSpec(
            "FLEX", RecordLevel.TEST, FuelPhase.LIQUID,
            (TableSpec("PSI-69_Experimental table_FLEX.csv", (
                Meta("FLEX Test #", "test_point_id"),
                Meta("FLEX Identifier", "flex_identifier"),
                Meta("Test Date", "test_date"),
                Meta("Test GMT", "test_time_gmt"),
                Text("Fuel", "fuel_name"),
                Num("Ambient pressure; mmHg", "pressure", "mmHg", fixup=zero_pressure_as_missing),
                # subscripts were lost in the source encoding: O=O2, N=N2, CO=CO2
                Num("O initial ambient composition; mole fraction", "o2", "mole fraction"),
                Num("N initial ambient composition; mole fraction", "n2", "mole fraction"),
                Num("CO initial ambient composition; mole fraction", "co2", "mole fraction"),
                Num("He initial ambient composition; mole fraction", "he", "mole fraction"),
                Num("Droplet initial diameter; mm", "droplet_initial_diameter", "mm"),
                Num("Visible flame extinction diameter; mm", "flame_extinction_diameter", "mm",
                    fixup=zero_extinction_on_disruption),
                # header says "mm" but the d²-law burning-rate constant is mm²/s (values 0.4-0.7)
                Num("Burning rate; mm", "burning_rate_constant", "mm2/s"),
                Num("Burn time; s", "burn_time", "s"),
                Text("Test end", "test_outcome"),
            ), AMBIENT_O2),),
        ),
        AdapterSpec(
            "FLEX-2", RecordLevel.TEST_MATRIX, FuelPhase.LIQUID,
            (TableSpec("PSI-68_Experimental table_Flex2.csv", (
                Text("Sample (Fuel Type)", "fuel_name"),
                Num("Initial Droplet Diameter (mm)", "droplet_initial_diameter", "mm", ranged=True),
                Text("Ambient Gas Mixture", "diluent"),
                Num("Oxygen Mole Fraction", "o2", "mole fraction"),
                Num("Ambient Pressure (atm)", "pressure", "atm"),
                Num("Ambient Temperature (C)", "ambient_temperature", "C"),
                Num("Flow Velocity (cm/s)", "flow_speed", "cm/s"),
            ), AMBIENT_O2),),
        ),
        AdapterSpec(
            "CFI", RecordLevel.TEST, FuelPhase.LIQUID,
            (TableSpec("PSI-39_Experimental table_CFI.csv", (
                Meta("Flex Number", "flex_number"),  # rows 81-88 repeat rows 24-31: ids are row-based
                Meta("Test Date", "test_date"),
                Meta("Local Time", "test_local_time"),
                Meta("CIR", "cir_run_identifier"),
                Num("Pressure", "pressure", "atm"),
                Num("Oxygen", "o2", "mole fraction"),
                Num("Nitrogen", "n2", "mole fraction", fixup=composition_not_closed),
                Num("Helium", "he", "mole fraction"),
                Text("Fiber", "fiber_supported_droplet"),
                Text("Fuel", "fuel_name"),
            ), AMBIENT_O2),),
        ),
        AdapterSpec(
            "ACME-BRE", RecordLevel.TEST_DAY, FuelPhase.GAS,
            (TableSpec("PSI-20_Experimental table_ACME BRE.csv", (
                Meta("Year", "test_year"),
                Meta("Month", "test_month"),
                Meta("Date", "test_day_of_month"),
                Num("Burner Size (mm)", "burner_size", "mm"),
                Text("Fuel Bottle", "fuel_name"),
                Num("Oxygen Conc (percent)", "o2", "%", fixup=excel_percent_artifact),
                Num("Flames Ignited", "flames_ignited", None),
            ), AMBIENT_O2),),
            notes_header="Notes",
        ),
        AdapterSpec(
            "ACME-CFI-G", RecordLevel.TEST, FuelPhase.GAS,
            (
                TableSpec("PSI-159_Experimental table_CFI-G_Normal Flames.csv", (
                    *_CFI_G_SHARED,
                    Text("Cool flame?", "cool_flame_observed"),
                    Num("XO2 before test", "o2", "fraction"),
                    Num("XO2 after test", "o2_after_test", "fraction"),
                    Num("Xf", "burner_fuel_fraction", "fraction"),
                    Num("mHC (mg/s)", "fuel_mass_flow_rate", "mg/s"),
                    Text("Self-ext or flow term", "termination_mode"),
                    Num("Peak burner T (C )", "peak_burner_temperature", "C"),
                ), AMBIENT_O2),
                TableSpec("PSI-159_Experimental table_CFI-G_Inverse Flames.csv", (
                    *_CFI_G_SHARED,
                    Num("Xf before test", "ambient_fuel_fraction", "fraction"),
                    Num("Xf after test", "ambient_fuel_fraction_after_test", "fraction"),
                    Num("XO2", "o2", "fraction"),
                    Num("HC burnrate (mg/s)", "fuel_mass_flow_rate", "mg/s"),
                    Num("O2 flow rate (mg/s)", "oxygen_mass_flow_rate", "mg/s"),
                    Text("Self -ext or flow term", "termination_mode"),
                    Skip("Peak burner Temp (C)", "same measurement as 'Peak burner temp (K)', kept in kelvin"),
                    Num("Peak burner temp (K)", "peak_burner_temperature", "K"),
                    Text("Color", "flame_color"),
                ), {"o2_basis": Constant("oxidizer_stream", "inverse flame: O2/N2 issues from the burner")}),
            ),
        ),
        AdapterSpec(
            "ACME-E-FIELD", RecordLevel.TEST_DAY, FuelPhase.GAS,
            (TableSpec("PSI-22_Experimental table_ACME E-FIELD Flames.csv", (
                Text("Test Type", "burner_campaign"),
                Meta("Test Day", "test_day_yyddd"),
                Meta("Year", "test_year"),
                Meta("Month", "test_month"),
                Meta("Date", "test_day_of_month"),
                Text("Mesh Polarity", "electrode_polarity"),
                Text("Fuel Bottle", "fuel_name"),
                Num("Fuel Conc", "fuel_concentration", "%", ranged=True),
                Num("Flames Ignited", "flames_ignited", None),
            )),),
            notes_header="Notes",
            continuation_header="Fuel Conc",
        ),
        AdapterSpec(
            "SPICE", RecordLevel.TEST, FuelPhase.GAS,
            (TableSpec("PSI-107_Experimental table_Spice.csv", (
                Meta("GMT date", "gmt_day_of_year"),
                Meta("GMT ignition", "gmt_ignition_time"),
                Meta("GMT Flame Off", "gmt_flame_off_time"),
                Text("Fuel", "fuel_name"),
                Num("Nozzle (mm)", "nozzle_diameter", "mm"),
                Num("Fuel Rate (sccm)", "fuel_volume_flow_rate", "sccm"),
                Num("Fuel Rate (mg/s)", "fuel_mass_flow_rate", "mg/s", fixup=spice_mass_flow_density_mismatch),
                Num("HC Fuel Rate (mg/s)", "hydrocarbon_mass_flow_rate", "mg/s",
                    fixup=spice_mass_flow_density_mismatch),
                Num("Air Rate (cm/s)", "flow_speed", "cm/s", fixup=negative_reading_as_missing),
            ), {"flow_direction": Constant("coflow", "SPICE = Smoke Point In Co-flow Experiment; air is coflow")}),),
        ),
        AdapterSpec(
            "SLICE", RecordLevel.TEST_DAY, FuelPhase.GAS,
            (TableSpec("PSI-106_Experimental table_Slice.csv", (
                Meta("Test Date", "test_date_and_remarks"),
                Text("Fuel Type", "fuel_name"),
            )),),
        ),
    )
}
