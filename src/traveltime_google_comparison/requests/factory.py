from typing import Dict

from traveltime_google_comparison.collect import TOMTOM_API, TRAVELTIME_API, GOOGLE_API
from traveltime_google_comparison.config import (
    retrieve_google_api_key,
    retrieve_tomtom_api_key,
    retrieve_traveltime_credentials,
)
from traveltime_google_comparison.requests.base_handler import BaseRequestHandler
from traveltime_google_comparison.requests.google_handler import GoogleRequestHandler
from traveltime_google_comparison.requests.tomtom_handler import TomTomRequestHandler
from traveltime_google_comparison.requests.traveltime_handler import (
    TravelTimeRequestHandler,
)


def initialize_request_handlers(
    google_max_rpm, tomtom_max_rpm, traveltime_max_rpm
) -> Dict[str, BaseRequestHandler]:
    google_api_key = retrieve_google_api_key()
    tomtom_api_key = retrieve_tomtom_api_key()
    credentials = retrieve_traveltime_credentials()
    return {
        GOOGLE_API: GoogleRequestHandler(google_api_key, google_max_rpm),
        TOMTOM_API: TomTomRequestHandler(tomtom_api_key, tomtom_max_rpm),
        TRAVELTIME_API: TravelTimeRequestHandler(
            credentials.app_id, credentials.api_key, traveltime_max_rpm
        ),
    }
