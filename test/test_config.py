import pytest

from traveltime_google_comparison.config import (
    Provider,
    Providers,
    parse_json_to_providers,
)
from traveltime_google_comparison.requests.traveltime_credentials import (
    Credentials,
)


def test_json_config_parse():
    json = """
        {
          "traveltime": {
            "app-id": "<your-app-id>",
            "api-key": "<your-api-key>",
            "max-rpm": "60"
          },
          "api-providers": [
            {
              "name": "google",
              "enabled": true,
              "api-key": "<your-api-key>",
              "max-rpm": "60"
            },
            {
              "name": "tomtom",
              "enabled": false,
              "api-key": "<your-api-key>",
              "max-rpm": "30"
            }
          ]
        }
    """

    providers = parse_json_to_providers(json)

    assert providers == Providers(
        base=Provider(
            name="traveltime",
            max_rpm=60,
            credentials=Credentials(app_id="<your-app-id>", api_key="<your-api-key>"),
        ),
        competitors=[
            Provider(
                name="google", max_rpm=60, credentials=Credentials("<your-api-key>")
            )
        ],
    )


def test_json_config_parse_all_disabled_providers():
    json = """
        {
          "traveltime": {
            "app-id": "<your-app-id>",
            "api-key": "<your-api-key>",
            "max-rpm": "60"
          },
          "api-providers": [
            {
              "name": "google",
              "enabled": false,
              "api-key": "<your-api-key>",
              "max-rpm": "60"
            },
            {
              "name": "tomtom",
              "enabled": false,
              "api-key": "<your-api-key>",
              "max-rpm": "30"
            }
          ]
        }
    """

    with pytest.raises(ValueError) as excinfo:
        _ = parse_json_to_providers(json)

    assert (
        str(excinfo.value)
        == "There should be at least one enabled API provider that's not TravelTime."
    )


def test_json_config_parse_empty_providers():
    json = """
        {
          "traveltime": {
            "app-id": "<your-app-id>",
            "api-key": "<your-api-key>",
            "max-rpm": "60"
          },
          "api-providers": []
        }
    """

    with pytest.raises(ValueError) as excinfo:
        _ = parse_json_to_providers(json)

    assert (
        str(excinfo.value)
        == "There should be at least one enabled API provider that's not TravelTime."
    )
