import logging
from dataclasses import dataclass
from typing import List

from pandas import DataFrame

from traveltime_google_comparison.collect import (
    TOMTOM_API,
    Fields,
    GOOGLE_API,
    TRAVELTIME_API,
)


def absolute_error(compare_to: str) -> str: return f"absolute_error_{compare_to}"
def relative_error(compare_to: str) -> str: return f"error_percentage_{compare_to}"


@dataclass
class QuantileErrorResult:
    absolute_error: int
    relative_error: int


def run_analysis(results: DataFrame, output_file: str, quantile: float):
    results_with_differences = calculate_differences(results, [GOOGLE_API, TOMTOM_API])

    logging.info(
        f"Mean relative error compared to Google API: {results_with_differences[relative_error(GOOGLE_API)].mean():.2f}%"
    )
    quantile_errors = calculate_quantiles(
        results_with_differences, quantile, GOOGLE_API
    )
    logging.info(
        f"{int(quantile * 100)}% of TravelTime results differ from Google API "
        f"by less than {int(quantile_errors.relative_error)}%"
    )

    logging.info(
        f"Mean relative error compared to TomTom API: {results_with_differences[relative_error(TOMTOM_API)].mean():.2f}%"
    )
    quantile_errors = calculate_quantiles(
        results_with_differences, quantile, TOMTOM_API
    )
    logging.info(
        f"{int(quantile * 100)}% of TravelTime results differ from TomTom API "
        f"by less than {int(quantile_errors.relative_error)}%"
    )

    logging.info(f"Detailed results can be found in {output_file} file")

    results_with_differences = results_with_differences.drop(
        columns=[absolute_error(GOOGLE_API)]
    )
    results_with_differences = results_with_differences.drop(
        columns=[absolute_error(TOMTOM_API)]
    )

    results_with_differences[relative_error(GOOGLE_API)] = results_with_differences[
       relative_error(GOOGLE_API) 
    ].astype(int)
    results_with_differences[relative_error(TOMTOM_API)] = results_with_differences[
       relative_error(TOMTOM_API) 
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
    compare_to: str,
) -> QuantileErrorResult:
    quantile_absolute_error = results_with_differences[absolute_error(compare_to)].quantile(
        quantile, "higher"
    )
    quantile_relative_error = results_with_differences[relative_error(compare_to)].quantile(
        quantile, "higher"
    )
    return QuantileErrorResult(
        int(quantile_absolute_error), int(quantile_relative_error)
    )
