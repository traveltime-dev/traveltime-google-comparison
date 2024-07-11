import argparse
import logging
import os
from enum import Enum

import pandas

from traveltime_google_comparison.requests.traveltime_credentials import TravelTimeCredentials

DEFAULT_GOOGLE_RPM = 60
DEFAULT_TRAVELTIME_RPM = 60

GOOGLE_API_KEY_VAR_NAME = "GOOGLE_API_KEY"
TRAVELTIME_APP_ID_VAR_NAME = "TRAVELTIME_APP_ID"
TRAVELTIME_API_KEY_VAR_NAME = "TRAVELTIME_API_KEY"

pandas.set_option('display.max_columns', None)
pandas.set_option('display.width', None)


class Mode(Enum):
    DRIVING = 'driving'
    PUBLIC_TRANSPORT = 'public_transport'


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fetch and compare travel times from Google Directions API and TravelTime Routes API")
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--output", required=True, help="Output CSV file path")
    parser.add_argument("--date", required=True, help="Date (YYYY-MM-DD)")
    parser.add_argument("--start-time", required=True, help="Start time (HH:MM)")
    parser.add_argument("--end-time", required=True, help="End time (HH:MM)")
    parser.add_argument("--interval", required=True, type=int, help="Interval in minutes")
    parser.add_argument("--time-zone-id", required=True, help="Non-abbreviated time zone identifier e.g. Europe/London")
    parser.add_argument("--google-max-rpm", required=False, type=int, default=DEFAULT_GOOGLE_RPM,
                        help="Maximum number of requests sent to Google API per minute")
    parser.add_argument("--traveltime-max-rpm", required=False, type=int, default=DEFAULT_TRAVELTIME_RPM,
                        help="Maximum number of requests sent to TravelTime API per minute")
    parser.add_argument("--skip-data-gathering", action=argparse.BooleanOptionalAction,
                        help="If set, reads already gathered data from input file and skips data gathering. Input file must conform to the output file format.")
    return parser.parse_args()


def retrieve_google_api_key():
    google_api_key = os.environ.get(GOOGLE_API_KEY_VAR_NAME)

    if not google_api_key:
        raise ValueError(f"{GOOGLE_API_KEY_VAR_NAME} not set in environment variables.")
    return google_api_key


def retrieve_traveltime_credentials() -> TravelTimeCredentials:
    app_id = os.environ.get(TRAVELTIME_APP_ID_VAR_NAME)
    api_key = os.environ.get(TRAVELTIME_API_KEY_VAR_NAME)

    if not (app_id and api_key):
        raise ValueError("TravelTime API credentials are missing from environment variables.")
    return TravelTimeCredentials(app_id, api_key)
