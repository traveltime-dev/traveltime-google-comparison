from datetime import datetime
from typing import Union
import logging

from traveltimepy import (
    Location,
    Coordinates,
    TravelTimeSdk,
    Driving,
    Property,
    PublicTransport,
)
from traveltimepy.dto.common import Snapping, SnappingPenalty, SnappingAcceptRoads

from traveltime_google_comparison.config import Mode
from traveltime_google_comparison.requests.base_handler import (
    BaseRequestHandler,
    RequestResult,
    create_async_limiter,
)

logger = logging.getLogger(__name__)


class TravelTimeRequestHandler(BaseRequestHandler):
    ORIGIN_ID = "o"
    DESTINATION_ID = "d"

    def __init__(self, app_id, api_key, max_rpm):
        self.sdk = TravelTimeSdk(
            app_id=app_id, api_key=api_key, user_agent="Travel Time Comparison Tool"
        )
        self._rate_limiter = create_async_limiter(max_rpm)

    async def send_request(
        self,
        origin: Coordinates,
        destination: Coordinates,
        departure_time: datetime,
        mode: Mode,
    ) -> RequestResult:
        locations = [
            Location(id=self.ORIGIN_ID, coords=origin),
            Location(id=self.DESTINATION_ID, coords=destination),
        ]
        results = None
        try:
            results = await self.sdk.routes_async(
                locations=locations,
                search_ids={
                    self.ORIGIN_ID: [self.DESTINATION_ID],
                },
                transportation=get_traveltime_specific_mode(mode),
                departure_time=departure_time,
                properties=[Property.TRAVEL_TIME],
                snapping=Snapping(
                    penalty=SnappingPenalty.DISABLED,
                    accept_roads=SnappingAcceptRoads.BOTH_DRIVABLE_AND_WALKABLE,
                ),
            )
        except Exception as e:
            logger.error(f"Exception during requesting TravelTime API, {e}")
            return RequestResult(None)

        if (
            not results
            or not results[0].locations
            or not results[0].locations[0].properties
        ):
            return RequestResult(None)

        properties = results[0].locations[0].properties[0]
        return RequestResult(travel_time=properties.travel_time)


class RouteNotFoundError(Exception):
    pass


def get_traveltime_specific_mode(mode: Mode) -> Union[Driving, PublicTransport]:
    if mode.value == Mode.DRIVING.value:
        return Driving()
    elif mode.value == Mode.PUBLIC_TRANSPORT.value:
        return PublicTransport()
    else:
        raise ValueError(f"Unsupported mode `{mode.value}`")
