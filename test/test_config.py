import pytest

from traveltime_google_comparison.config import (
    TRAVELTIME_APP_ID_VAR_NAME,
    TRAVELTIME_API_KEY_VAR_NAME,
    retrieve_traveltime_credentials,
)
from traveltime_google_comparison.requests.traveltime_credentials import (
    TravelTimeCredentials,
)


def test_retrieve_traveltime_credentials_valid(monkeypatch):
    monkeypatch.setenv(TRAVELTIME_APP_ID_VAR_NAME, "sample_app_id")
    monkeypatch.setenv(TRAVELTIME_API_KEY_VAR_NAME, "sample_api_key")

    credentials = retrieve_traveltime_credentials()

    assert isinstance(credentials, TravelTimeCredentials)
    assert credentials.app_id == "sample_app_id"
    assert credentials.api_key == "sample_api_key"


def test_retrieve_traveltime_credentials_missing_app_id(monkeypatch):
    monkeypatch.delenv(TRAVELTIME_APP_ID_VAR_NAME, raising=False)
    monkeypatch.setenv(TRAVELTIME_API_KEY_VAR_NAME, "sample_api_key")

    with pytest.raises(
        ValueError,
        match="TravelTime API credentials are missing from environment variables.",
    ):
        retrieve_traveltime_credentials()


def test_retrieve_traveltime_credentials_missing_api_key(monkeypatch):
    monkeypatch.setenv(TRAVELTIME_APP_ID_VAR_NAME, "sample_app_id")
    monkeypatch.delenv(TRAVELTIME_API_KEY_VAR_NAME, raising=False)

    with pytest.raises(
        ValueError,
        match="TravelTime API credentials are missing from environment variables.",
    ):
        retrieve_traveltime_credentials()


def test_retrieve_traveltime_credentials_missing_both(monkeypatch):
    monkeypatch.delenv(TRAVELTIME_APP_ID_VAR_NAME, raising=False)
    monkeypatch.delenv(TRAVELTIME_API_KEY_VAR_NAME, raising=False)

    with pytest.raises(
        ValueError,
        match="TravelTime API credentials are missing from environment variables.",
    ):
        retrieve_traveltime_credentials()
