from typing import Dict

from traveltime_google_comparison.collect import (
    TOMTOM_API,
    HERE_API,
    MAPBOX_API,
    OSRM_API,
    TRAVELTIME_API,
    GOOGLE_API,
    OPENROUTES_API,
)
from traveltime_google_comparison.config import Provider, Providers
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


def initialize_request_handlers(providers: Providers) -> Dict[str, BaseRequestHandler]:
    def create_google_handler(provider: Provider):
        return GoogleRequestHandler(provider.credentials.api_key, provider.max_rpm)

    def create_tomtom_handler(provider: Provider):
        return TomTomRequestHandler(provider.credentials.api_key, provider.max_rpm)

    def create_here_handler(provider: Provider):
        return HereRequestHandler(provider.credentials.api_key, provider.max_rpm)

    def create_osrm_handler(provider: Provider):
        return OSRMRequestHandler("", provider.max_rpm)

    def create_openroutes_handler(provider: Provider):
        return OpenRoutesRequestHandler(provider.credentials.api_key, provider.max_rpm)

    def create_mapbox_handler(provider: Provider):
        return MapboxRequestHandler(provider.credentials.api_key, provider.max_rpm)

    def create_traveltime_handler(provider: Provider):
        return TravelTimeRequestHandler(
            provider.credentials.app_id, provider.credentials.api_key, provider.max_rpm
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
    for competitor in providers.competitors:
        if competitor.name in handler_mapping:
            handlers[competitor.name] = handler_mapping[competitor.name](competitor)

    # Always add TRAVELTIME_API handler
    handlers[TRAVELTIME_API] = create_traveltime_handler(providers.base)

    return handlers
