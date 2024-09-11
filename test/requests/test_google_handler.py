from enum import Enum

import pytest

from traveltime_google_comparison.config import Mode
from traveltime_google_comparison.requests.google_handler import (
    get_google_specific_mode,
)


def test_get_google_specific_mode_for_driving():
    result = get_google_specific_mode(Mode.DRIVING)
    assert result == "driving"


def test_get_google_specific_mode_for_public_transport():
    result = get_google_specific_mode(Mode.PUBLIC_TRANSPORT)
    assert result == "transit"


def test_get_google_specific_mode_for_unsupported_mode():
    class MockMode(Enum):
        WALKING = "WALKING"

    with pytest.raises(ValueError, match=r"Unsupported mode: `WALKING`"):
        get_google_specific_mode(MockMode.WALKING)
