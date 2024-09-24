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
)
from traveltime_google_comparison.requests import factory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


async def run():
    providers = [GOOGLE_API, TOMTOM_API, HERE_API, MAPBOX_API, OSRM_API, OPENROUTES_API]
    args = config.parse_args()
    csv = pd.read_csv(
        args.input, usecols=[Fields.ORIGIN, Fields.DESTINATION]
    ).drop_duplicates()

    if len(csv) == 0:
        logger.info("Provided input file is empty. Exiting.")
        return

    request_handlers = factory.initialize_request_handlers(
        args.google_max_rpm,
        args.tomtom_max_rpm,
        args.here_max_rpm,
        args.osrm_max_rpm,
        args.openroutes_max_rpm,
        args.mapbox_max_rpm,
        args.traveltime_max_rpm,
    )
    if args.skip_data_gathering:
        travel_times_df = pd.read_csv(
            args.input,
            usecols=[
                Fields.ORIGIN,
                Fields.DESTINATION,
                Fields.DEPARTURE_TIME,
                Fields.TRAVEL_TIME[GOOGLE_API],
                Fields.TRAVEL_TIME[TOMTOM_API],
                Fields.TRAVEL_TIME[HERE_API],
                Fields.TRAVEL_TIME[OSRM_API],
                Fields.TRAVEL_TIME[OPENROUTES_API],
                Fields.TRAVEL_TIME[MAPBOX_API],
                Fields.TRAVEL_TIME[TRAVELTIME_API],
            ],
        )
    else:
        travel_times_df = await collect.collect_travel_times(
            args, csv, request_handlers, providers
        )
    filtered_travel_times_df = travel_times_df.loc[
        travel_times_df[Fields.TRAVEL_TIME[GOOGLE_API]].notna()
        & travel_times_df[Fields.TRAVEL_TIME[TOMTOM_API]].notna()
        & travel_times_df[Fields.TRAVEL_TIME[HERE_API]].notna()
        & travel_times_df[Fields.TRAVEL_TIME[OSRM_API]].notna()
        & travel_times_df[Fields.TRAVEL_TIME[OPENROUTES_API]].notna()
        & travel_times_df[Fields.TRAVEL_TIME[MAPBOX_API]].notna()
        & travel_times_df[Fields.TRAVEL_TIME[TRAVELTIME_API]].notna(),
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
