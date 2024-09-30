import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Optional

import pandas as pd
import pytz
from pandas import DataFrame
from pytz.tzinfo import BaseTzInfo
from traveltimepy import Coordinates

from traveltime_google_comparison.config import Mode
from traveltime_google_comparison.requests.base_handler import BaseRequestHandler


GOOGLE_API = "google"
TOMTOM_API = "tomtom"
HERE_API = "here"
OSRM_API = "osrm"
MAPBOX_API = "mapbox"
TRAVELTIME_API = "traveltime"
OPENROUTES_API = "openroutes"


def get_capitalized_provider_name(provider: str) -> str:
    if provider == "google":
        return "Google"
    elif provider == "tomtom":
        return "TomTom"
    elif provider == "here":
        return "HERE"
    elif provider == "osrm":
        return "OSRM"
    elif provider == "openroutes":
        return "OpenRoutes"
    elif provider == "mapbox":
        return "Mapbox"
    elif provider == "traveltime":
        return "TravelTime"
    else:
        raise ValueError(f"Unsupported API provider: {provider}")


@dataclass
class Fields:
    ORIGIN = "origin"
    DESTINATION = "destination"
    DEPARTURE_TIME = "departure_time"
    TRAVEL_TIME = {
        GOOGLE_API: "google_travel_time",
        TOMTOM_API: "tomtom_travel_time",
        HERE_API: "here_travel_time",
        OSRM_API: "osrm_travel_time",
        MAPBOX_API: "mapbox_travel_time",
        OPENROUTES_API: "openroutes_travel_time",
        TRAVELTIME_API: "tt_travel_time",
    }


logger = logging.getLogger(__name__)


async def fetch_travel_time(
    origin: str,
    destination: str,
    api: str,
    departure_time: datetime,
    request_handler: BaseRequestHandler,
    mode: Mode,
) -> Dict[str, str]:
    origin_coord = parse_coordinates(origin)
    destination_coord = parse_coordinates(destination)

    async with request_handler.rate_limiter:
        logger.debug(
            f"Sending request to {api} for {origin_coord}, {destination_coord}, {departure_time}"
        )
        result = await request_handler.send_request(
            origin_coord, destination_coord, departure_time, mode
        )
        logger.debug(
            f"Finished request to {api} for {origin_coord}, {destination_coord}, {departure_time}"
        )
        return wrap_result(origin, destination, result.travel_time, departure_time, api)


def parse_coordinates(coord_string: str) -> Coordinates:
    lat, lng = [c.strip() for c in coord_string.split(",")]
    return Coordinates(lat=float(lat), lng=float(lng))


def wrap_result(
    origin: str,
    destination: str,
    travel_time: Optional[int],
    departure_time: datetime,
    api: str,
):
    return {
        Fields.ORIGIN: origin,
        Fields.DESTINATION: destination,
        Fields.DEPARTURE_TIME: departure_time.strftime("%Y-%m-%d %H:%M:%S%z"),
        Fields.TRAVEL_TIME[api]: travel_time,
    }


def localize_datetime(date: str, time: str, timezone: BaseTzInfo) -> datetime:
    datetime_instance = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    return timezone.localize(datetime_instance)


def generate_tasks(
    data: DataFrame,
    time_instants: List[datetime],
    request_handlers: Dict[str, BaseRequestHandler],
    mode: Mode,
) -> list:
    tasks = []
    for index, row in data.iterrows():
        for time_instant in time_instants:
            for api, request_handler in request_handlers.items():
                task = fetch_travel_time(
                    row[Fields.ORIGIN],
                    row[Fields.DESTINATION],
                    api,
                    time_instant,
                    request_handler,
                    mode=mode,
                )
                tasks.append(task)
    return tasks


async def collect_travel_times(
    args,
    data,
    request_handlers: Dict[str, BaseRequestHandler],
    provider_names: List[str],
) -> DataFrame:
    timezone = pytz.timezone(args.time_zone_id)
    localized_start_datetime = localize_datetime(args.date, args.start_time, timezone)
    localized_end_datetime = localize_datetime(args.date, args.end_time, timezone)
    time_instants = generate_time_instants(
        localized_start_datetime, localized_end_datetime, args.interval
    )

    tasks = generate_tasks(data, time_instants, request_handlers, mode=Mode.DRIVING)

    capitalized_providers_str = ", ".join(
        [get_capitalized_provider_name(provider) for provider in provider_names]
    )
    logger.info(f"Sending {len(tasks)} requests to {capitalized_providers_str} APIs")

    results = await asyncio.gather(*tasks)

    results_df = pd.DataFrame(results)
    deduplicated = results_df.groupby(
        [Fields.ORIGIN, Fields.DESTINATION, Fields.DEPARTURE_TIME], as_index=False
    ).agg({Fields.TRAVEL_TIME[provider]: "first" for provider in provider_names})
    deduplicated.to_csv(args.output, index=False)
    return deduplicated


def generate_time_instants(
    start_time: datetime, end_time: datetime, interval: int
) -> List[datetime]:
    if start_time > end_time:
        raise ValueError("Start time must be before end time.")
    current_time = start_time
    results = []
    while current_time <= end_time:
        results.append(current_time)
        current_time += timedelta(minutes=interval)
    return results
