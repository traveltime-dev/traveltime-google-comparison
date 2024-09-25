from argparse import Namespace
from typing import Dict, List

from traveltime_google_comparison.collect import (
    TOMTOM_API,
    HERE_API,
    MAPBOX_API,
    OSRM_API,
    TRAVELTIME_API,
    GOOGLE_API,
    OPENROUTES_API,
)
from traveltime_google_comparison.config import (
    retrieve_google_api_key,
    retrieve_here_api_key,
    retrieve_mapbox_api_key,
    retrieve_tomtom_api_key,
    retrieve_openroutes_api_key,
    retrieve_traveltime_credentials,
)
from traveltime_google_comparison.requests.base_handler import BaseRequestHandler
from traveltime_google_comparison.requests.google_handler import GoogleRequestHandler
from traveltime_google_comparison.requests.tomtom_handler import TomTomRequestHandler
from traveltime_google_comparison.requests.here_handler import HereRequestHandler
from traveltime_google_comparison.requests.osrm_handler import OSRMRequestHandler
from traveltime_google_comparison.requests.mapbox_handler import MapboxRequestHandler
from traveltime_google_comparison.requests.openroutes_handler import (
    OpenRoutesRequestHandler,
)
from traveltime_google_comparison.requests.traveltime_handler import (
    TravelTimeRequestHandler,
)


def initialize_request_handlers(
    providers: List[str], args: Namespace
) -> Dict[str, BaseRequestHandler]:
    def create_google_handler():
        return GoogleRequestHandler(retrieve_google_api_key(), args.google_max_rpm)

    def create_tomtom_handler():
        return TomTomRequestHandler(retrieve_tomtom_api_key(), args.tomtom_max_rpm)

    def create_here_handler():
        return HereRequestHandler(retrieve_here_api_key(), args.here_max_rpm)

    def create_osrm_handler():
        return OSRMRequestHandler("", args.osrm_max_rpm)

    def create_openroutes_handler():
        return OpenRoutesRequestHandler(
            retrieve_openroutes_api_key(), args.openroutes_max_rpm
        )

    def create_mapbox_handler():
        return MapboxRequestHandler(retrieve_mapbox_api_key(), args.mapbox_max_rpm)

    def create_traveltime_handler():
        credentials = retrieve_traveltime_credentials()
        return TravelTimeRequestHandler(
            credentials.app_id, credentials.api_key, args.traveltime_max_rpm
        )

    handler_mapping = {
        GOOGLE_API: create_google_handler,
        TOMTOM_API: create_tomtom_handler,
        HERE_API: create_here_handler,
        OSRM_API: create_osrm_handler,
        OPENROUTES_API: create_openroutes_handler,
        MAPBOX_API: create_mapbox_handler,
    }

    handlers = {}
    for provider in providers:
        if provider in handler_mapping:
            handlers[provider] = handler_mapping[provider]()

    # Always add TRAVELTIME_API handler
    handlers[TRAVELTIME_API] = create_traveltime_handler()

    return handlers
