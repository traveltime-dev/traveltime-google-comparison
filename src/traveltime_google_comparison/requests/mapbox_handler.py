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


class MapboxApiError(Exception):
    pass


class MapboxRequestHandler(BaseRequestHandler):
    MAPBOX_ROUTES_URL = "https://api.mapbox.com/directions/v5/mapbox"

    default_timeout = aiohttp.ClientTimeout(total=60)

    def __init__(self, api_key, max_rpm):
        self.api_key = api_key
        self._rate_limiter = create_async_limiter(max_rpm)

    async def send_request(
        self,
        origin: Coordinates,
        destination: Coordinates,
        departure_time: datetime,
        mode: Mode = Mode.DRIVING,
    ) -> RequestResult:
        route = f"{origin.lng},{origin.lat};{destination.lng},{destination.lat}"  # for Mapbox lat/lng are flipped!
        transport_mode = get_mapbox_specific_mode(mode)
        params = {
            "depart_at": departure_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "access_token": self.api_key,
            "exclude": "ferry",  # by default I think it includes ferries, but for our API we use just driving, without ferries
        }
        try:
            async with aiohttp.ClientSession(
                timeout=self.default_timeout
            ) as session, session.get(
                f"{self.MAPBOX_ROUTES_URL}/{transport_mode}/{route}", params=params
            ) as response:
                data = await response.json()
                if response.status == 200:
                    duration = data["routes"][0]["duration"]
                    if not duration:
                        raise MapboxApiError(
                            "No route found between origin and destination."
                        )
                    return RequestResult(travel_time=int(duration))
                else:
                    error_message = data.get("detailedError", "")
                    logger.error(
                        f"Error in Mapbox API response: {response.status} - {error_message}"
                    )
                    return RequestResult(None)
        except Exception as e:
            logger.error(f"Exception during requesting Mapbox API, {e}")
            return RequestResult(None)


def get_mapbox_specific_mode(mode: Mode) -> str:
    if mode == Mode.DRIVING:
        return "driving-traffic"
    elif mode == Mode.PUBLIC_TRANSPORT:
        raise ValueError("Public transport is not supported for Mapbox requests")
    else:
        raise ValueError(f"Unsupported mode: `{mode.value}`")
