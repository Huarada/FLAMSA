"""Deterministic, conditional least-squares estimates for experimental evidence."""

from dataclasses import dataclass
from math import isfinite, sqrt

import numpy as np
import scipy  # type: ignore[import-untyped]
from scipy.stats import spearmanr, t  # type: ignore[import-untyped]

MIN_OBSERVATIONS = 6
MIN_OXYGEN_LEVELS = 3
MIN_RESIDUAL_DF = 3
MAX_DESIGN_CONDITION = 10_000.0
CONFIDENCE_LEVEL = 0.95
LINE_SAMPLES = 41
CONSTANT_TOLERANCE = 1e-10
NUMERICAL_LIBRARY_VERSIONS = (("numpy", np.__version__), ("scipy", scipy.__version__))


@dataclass(frozen=True)
class MeanPrediction:
    oxygen_percent: float
    expected_k_mm2_s: float
    lower_k_mm2_s: float
    upper_k_mm2_s: float


@dataclass(frozen=True)
class OxygenSlope:
    observations: int
    residual_df: int
    slope_mm2_s_per_o2_point: float
    lower_slope: float
    upper_slope: float
    confidence_level: float
    raw_spearman_rho: float | None
    model_r_squared: float | None
    reference_conditions: tuple[tuple[str, float], ...]
    adjusted_covariates: tuple[str, ...]
    condition_number: float
    line: tuple[MeanPrediction, ...]


def oxygen_slope(oxygen: tuple[float, ...], k: tuple[float, ...],
                 controls: tuple[tuple[str, tuple[float, ...]], ...]) -> tuple[OxygenSlope | None, str | None]:
    """Fit within one fixed fuel/blend stratum; caller supplies reported scalars only."""
    count = len(oxygen)
    if len(k) != count or any(len(values) != count for _, values in controls):
        raise ValueError("Regression inputs must have equal lengths.")
    if any(not isfinite(value) for values in (oxygen, k, *(values for _, values in controls)) for value in values):
        raise ValueError("Regression inputs must be finite.")
    if count < MIN_OBSERVATIONS:
        return None, f"At least {MIN_OBSERVATIONS} observations are required."
    if len(set(oxygen)) < MIN_OXYGEN_LEVELS:
        return None, f"At least {MIN_OXYGEN_LEVELS} distinct oxygen levels are required."
    x, y = np.asarray(oxygen, dtype=float), np.asarray(k, dtype=float)
    varying = [(name, np.asarray(values, dtype=float)) for name, values in controls
               if max(values) - min(values) > CONSTANT_TOLERANCE]
    columns = [x, *(values for _, values in varying)]
    means = np.asarray([np.mean(values) for values in columns])
    scales = np.asarray([np.std(values) for values in columns])
    design = np.column_stack([np.ones(count), *((values - mean) / scale for values, mean, scale
                                               in zip(columns, means, scales, strict=True))])
    degrees = count - design.shape[1]
    if degrees < MIN_RESIDUAL_DF:
        return None, f"At least {MIN_RESIDUAL_DF} residual degrees of freedom are required."
    condition = float(np.linalg.cond(design))
    if np.linalg.matrix_rank(design) != design.shape[1] or condition > MAX_DESIGN_CONDITION:
        return None, "Oxygen and adjustment covariates cannot be separated reliably (collinear design)."
    coefficients, _, _, _ = np.linalg.lstsq(design, y, rcond=None)
    residual = y - design @ coefficients
    variance = float(residual @ residual) / degrees
    covariance = variance * np.linalg.inv(design.T @ design)
    critical = float(t.ppf((1 + CONFIDENCE_LEVEL) / 2, degrees))
    slope = float(coefficients[1] / scales[0])
    slope_error = sqrt(max(0.0, float(covariance[1, 1]))) / float(scales[0])
    predictions = []
    for oxygen_value in np.linspace(float(x.min()), float(x.max()), LINE_SAMPLES):
        row = np.zeros(design.shape[1])
        row[0], row[1] = 1, (oxygen_value - means[0]) / scales[0]
        expected = float(row @ coefficients)
        margin = critical * sqrt(max(0.0, float(row @ covariance @ row)))
        predictions.append(MeanPrediction(float(oxygen_value), expected, expected - margin, expected + margin))
    total_variation = float(np.sum((y - np.mean(y)) ** 2))
    rho = float(spearmanr(x, y).statistic) if len(set(k)) > 1 else None
    result = OxygenSlope(count, degrees, slope, slope - critical * slope_error, slope + critical * slope_error,
                         CONFIDENCE_LEVEL, rho, 1 - float(residual @ residual) / total_variation
                         if total_variation > 0 else None,
                         tuple((name, float(np.mean(values))) for name, values in controls),
                         tuple(name for name, _ in varying), condition, tuple(predictions))
    return result, None
