import logging
from datetime import datetime

import aiohttp
from traveltimepy import Coordinates

from traveltime_google_comparison.config import Mode
from traveltime_google_comparison.requests.base_handler import (
    BaseRequestHandler,
    RequestResult,
    create_async_limiter,
)

logger = logging.getLogger(__name__)


class GoogleApiError(Exception):
    pass


class GoogleRequestHandler(BaseRequestHandler):
    DURATION_IN_TRAFFIC = "duration_in_traffic"
    DURATION = "duration"
    GOOGLE_DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"

    default_timeout = aiohttp.ClientTimeout(total=60)

    def __init__(self, api_key, max_rpm):
        self.api_key = api_key
        self._rate_limiter = create_async_limiter(max_rpm)

    async def send_request(
        self,
        origin: Coordinates,
        destination: Coordinates,
        departure_time: datetime,
        mode: Mode,
    ) -> RequestResult:
        params = {
            "origin": "{},{}".format(origin.lat, origin.lng),
            "destination": "{},{}".format(destination.lat, destination.lng),
            "mode": get_google_specific_mode(mode),
            "traffic_model": "best_guess",
            "departure_time": int(departure_time.timestamp()),
            "key": self.api_key,
        }
        try:
            async with aiohttp.ClientSession(
                timeout=self.default_timeout
            ) as session, session.get(
                self.GOOGLE_DIRECTIONS_URL, params=params
            ) as response:
                data = await response.json()
                status = data["status"]

                if status == "OK":
                    route = data.get("routes", [{}])[0]
                    leg = route.get("legs", [{}])[0]

                    if not leg:
                        raise GoogleApiError(
                            "No route found between origin and destination."
                        )

                    travel_time = leg.get(
                        self.DURATION_IN_TRAFFIC, leg.get(self.DURATION)
                    )["value"]
                    return RequestResult(travel_time=travel_time)
                else:
                    error_message = data.get("error_message", "")
                    logger.error(
                        f"Error in Google API response: {status} - {error_message}"
                    )
                    return RequestResult(None)
        except Exception as e:
            logger.error(f"Exception during requesting Google API, {e}")
            return RequestResult(None)


def get_google_specific_mode(mode: Mode) -> str:
    if mode == Mode.DRIVING:
        return "driving"
    elif mode == Mode.PUBLIC_TRANSPORT:
        return "transit"
    else:
        raise ValueError(f"Unsupported mode: `{mode.value}`")
