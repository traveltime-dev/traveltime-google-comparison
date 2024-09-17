import logging
from dataclasses import dataclass
from typing import List

from pandas import DataFrame
import pandas

from traveltime_google_comparison.collect import (
    TOMTOM_API,
    Fields,
    GOOGLE_API,
    TRAVELTIME_API,
)


ABSOLUTE_ERROR_GOOGLE = "absolute_error_google"
RELATIVE_ERROR_GOOGLE = "error_percentage_google"
ABSOLUTE_ERROR_TOMTOM = "absolute_error_tomtom"
RELATIVE_ERROR_TOMTOM = "error_percentage_tomtom"


@dataclass
class QuantileErrorResult:
    absolute_error: int
    relative_error: int


def run_analysis(results: DataFrame, output_file: str, quantile: float):
    results_with_differences = calculate_differences(results, [GOOGLE_API, TOMTOM_API])

    logging.info(
        f"Mean relative error compared to Google API: {results_with_differences[RELATIVE_ERROR_GOOGLE].mean():.2f}%"
    )
    quantile_errors = calculate_quantiles(
        results_with_differences, quantile, ABSOLUTE_ERROR_GOOGLE
    )
    logging.info(
        f"{int(quantile * 100)}% of TravelTime results differ from Google API "
        f"by less than {int(quantile_errors.relative_error)}%"
    )

    logging.info(
        f"Mean relative error compared to TomTom API: {results_with_differences[RELATIVE_ERROR_TOMTOM].mean():.2f}%"
    )
    quantile_errors = calculate_quantiles(
        results_with_differences, quantile, ABSOLUTE_ERROR_TOMTOM
    )
    logging.info(
        f"{int(quantile * 100)}% of TravelTime results differ from TomTom API "
        f"by less than {int(quantile_errors.relative_error)}%"
    )

    logging.info(f"Detailed results can be found in {output_file} file")

    results_with_differences = results_with_differences.drop(
        columns=[ABSOLUTE_ERROR_GOOGLE]
    )
    results_with_differences = results_with_differences.drop(
        columns=[ABSOLUTE_ERROR_TOMTOM]
    )

    results_with_differences[RELATIVE_ERROR_GOOGLE] = results_with_differences[
        RELATIVE_ERROR_GOOGLE
    ].astype(int)
    results_with_differences[RELATIVE_ERROR_TOMTOM] = results_with_differences[
        RELATIVE_ERROR_TOMTOM
    ].astype(int)

    results_with_differences.to_csv(output_file, index=False)


def calculate_differences(results: DataFrame, providers: List[str]) -> DataFrame:
    results_with_differences = results.copy()

    for provider in providers:
        if provider != TRAVELTIME_API:
            absolute_error_col = f"absolute_error_{provider}"
            relative_error_col = f"error_percentage_{provider}"

            results_with_differences[absolute_error_col] = abs(
                results[Fields.TRAVEL_TIME[provider]]
                - results[Fields.TRAVEL_TIME[TRAVELTIME_API]]
            )

            results_with_differences[relative_error_col] = (
                results_with_differences[absolute_error_col]
                / results_with_differences[Fields.TRAVEL_TIME[provider]]
                * 100
            )

    return results_with_differences


def calculate_quantiles(
    results_with_differences: DataFrame,
    quantile: float,
    absolute_error_str: str,
) -> QuantileErrorResult:
    quantile_absolute_error = results_with_differences[absolute_error_str].quantile(
        quantile, "higher"
    )
    quantile_relative_error = results_with_differences[absolute_error_str].quantile(
        quantile, "higher"
    )
    return QuantileErrorResult(
        int(quantile_absolute_error), int(quantile_relative_error)
    )
