import logging
from dataclasses import dataclass

from pandas import DataFrame

from traveltime_google_comparison.collect import (
    Fields,
    TRAVELTIME_API,
    get_capitalized_provider_name,
)
from traveltime_google_comparison.config import Providers


def absolute_error(api_provider: str) -> str:
    return f"absolute_error_{api_provider}"


def relative_error(api_provider: str) -> str:
    return f"error_percentage_{api_provider}"


@dataclass
class QuantileErrorResult:
    absolute_error: int
    relative_error: int


def log_results(
    results_with_differences: DataFrame, quantile: float, api_providers: Providers
):
    for provider in api_providers.competitors:
        name = provider.name
        capitalized_provider = get_capitalized_provider_name(name)
        logging.info(
            f"Mean relative error compared to {capitalized_provider} "
            f"API: {results_with_differences[relative_error(name)].mean():.2f}%"
        )
        quantile_errors = calculate_quantiles(results_with_differences, quantile, name)
        logging.info(
            f"{int(quantile * 100)}% of TravelTime results differ from {capitalized_provider} API "
            f"by less than {int(quantile_errors.relative_error)}%"
        )


def format_results_for_csv(
    results_with_differences: DataFrame, api_providers: Providers
) -> DataFrame:
    formatted_results = results_with_differences.copy()

    for provider in api_providers.competitors:
        name = provider.name
        formatted_results = formatted_results.drop(columns=[absolute_error(name)])
        relative_error_col = relative_error(name)
        formatted_results[relative_error_col] = formatted_results[
            relative_error_col
        ].astype(int)

    return formatted_results


def run_analysis(
    results: DataFrame, output_file: str, quantile: float, api_providers: Providers
):
    results_with_differences = calculate_differences(results, api_providers)
    log_results(results_with_differences, quantile, api_providers)

    logging.info(f"Detailed results can be found in {output_file} file")

    formatted_results = format_results_for_csv(results_with_differences, api_providers)

    formatted_results.to_csv(output_file, index=False)


def calculate_differences(results: DataFrame, api_providers: Providers) -> DataFrame:
    results_with_differences = results.copy()

    for provider in api_providers.competitors:
        name = provider.name
        absolute_error_col = absolute_error(name)
        relative_error_col = relative_error(name)

        results_with_differences[absolute_error_col] = abs(
            results[Fields.TRAVEL_TIME[name]]
            - results[Fields.TRAVEL_TIME[TRAVELTIME_API]]
        )

        results_with_differences[relative_error_col] = (
            results_with_differences[absolute_error_col]
            / results_with_differences[Fields.TRAVEL_TIME[name]]
            * 100
        )

    return results_with_differences


def calculate_quantiles(
    results_with_differences: DataFrame,
    quantile: float,
    api_provider_name: str,
) -> QuantileErrorResult:
    quantile_absolute_error = results_with_differences[
        absolute_error(api_provider_name)
    ].quantile(quantile, "higher")
    quantile_relative_error = results_with_differences[
        relative_error(api_provider_name)
    ].quantile(quantile, "higher")
    return QuantileErrorResult(
        int(quantile_absolute_error), int(quantile_relative_error)
    )
