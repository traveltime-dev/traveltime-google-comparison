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


class TomTomApiError(Exception):
    pass


class TomTomRequestHandler(BaseRequestHandler):
    TOMTOM_ROUTING_URL = "https://api.tomtom.com/routing/1/calculateRoute/"

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
        route = f"{origin.lat},{origin.lng}:{destination.lat},{destination.lng}"
        params = {
            "key": self.api_key,
            "departAt": departure_time.isoformat(),
            "travelMode": get_tomtom_specific_mode(mode),
        }
        try:
            async with aiohttp.ClientSession(
                timeout=self.default_timeout
            ) as session, session.get(
                f"{self.TOMTOM_ROUTING_URL}{route}/json", params=params
            ) as response:
                data = await response.json()
                if response.status == 200:
                    travel_time = data["routes"][0]["summary"]["travelTimeInSeconds"]

                    if not travel_time:
                        raise TomTomApiError(
                            "No route found between origin and destination."
                        )

                    return RequestResult(travel_time=travel_time)
                else:
                    error_message = data.get("detailedError", "")
                    logger.error(
                        f"Error in TomTom API response: {response.status} - {error_message}"
                    )
                    return RequestResult(None)
        except Exception as e:
            logger.error(f"Exception during requesting TomTom API, {e}")
            return RequestResult(None)


def get_tomtom_specific_mode(mode: Mode) -> str:
    if mode == Mode.DRIVING:
        return "car"
    elif mode == Mode.PUBLIC_TRANSPORT:
        return "bus"  # TomTom doesn't have a general mode for transit / PT
        # TODO: figure out how to compare PT modes accorss different providers
    else:
        raise ValueError(f"Unsupported mode: `{mode.value}`")
