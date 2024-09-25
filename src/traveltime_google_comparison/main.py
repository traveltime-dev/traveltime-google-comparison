import asyncio
import logging

import pandas as pd

from traveltime_google_comparison import collect
from traveltime_google_comparison import config
from traveltime_google_comparison.analysis import run_analysis
from traveltime_google_comparison.collect import (
    OSRM_API,
    OPENROUTES_API,
    HERE_API,
    MAPBOX_API,
    Fields,
    GOOGLE_API,
    TRAVELTIME_API,
    TOMTOM_API,
    ALL_COMPETITORS,
)
from traveltime_google_comparison.requests import factory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


async def run():
    args = config.parse_args()

    # Get all providers that should be tested against TravelTime
    providers = [provider for provider in ALL_COMPETITORS if provider in args.providers]

    # TravelTime always should be in the analysis, unless in the future we decide to
    # allow the user to control what is the base for comparison.
    if TRAVELTIME_API not in providers:
        providers.append(TRAVELTIME_API)

    csv = pd.read_csv(
        args.input, usecols=[Fields.ORIGIN, Fields.DESTINATION]
    ).drop_duplicates()

    if len(csv) == 0:
        logger.info("Provided input file is empty. Exiting.")
        return

    request_handlers = factory.initialize_request_handlers(providers, args)
    if args.skip_data_gathering:
        travel_times_df = pd.read_csv(
            args.input,
            usecols=[
                Fields.ORIGIN,
                Fields.DESTINATION,
                Fields.DEPARTURE_TIME,
            ]  # base fields
            + [Fields.TRAVEL_TIME[provider] for provider in providers],  # all providers
        )
    else:
        travel_times_df = await collect.collect_travel_times(
            args, csv, request_handlers, providers
        )

    filtered_travel_times_df = travel_times_df.loc[
        travel_times_df[[Fields.TRAVEL_TIME[provider] for provider in providers]]
        .notna()
        .all(axis=1),
        :,
    ]

    filtered_rows = len(filtered_travel_times_df)
    if filtered_rows == 0:
        logger.info("All rows from the input file were skipped. Exiting.")
    else:
        all_rows = len(travel_times_df)
        skipped_rows = all_rows - filtered_rows
        if skipped_rows > 0:
            logger.info(
                f"Skipped {skipped_rows} rows ({100 * skipped_rows / all_rows:.2f}%)"
            )
        run_analysis(filtered_travel_times_df, args.output, 0.90, providers)


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
