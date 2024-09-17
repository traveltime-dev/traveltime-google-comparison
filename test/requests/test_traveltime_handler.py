from enum import Enum

import pytest
from traveltimepy import Driving, PublicTransport

from traveltime_google_comparison.config import Mode
from traveltime_google_comparison.requests.traveltime_handler import (
    get_traveltime_specific_mode,
)


def test_get_traveltime_specific_mode_for_driving():
    result = get_traveltime_specific_mode(Mode.DRIVING)
    assert result == Driving()


def test_get_traveltime_specific_mode_for_public_transport():
    result = get_traveltime_specific_mode(Mode.PUBLIC_TRANSPORT)
    assert result == PublicTransport()


def test_get_traveltime_specific_mode_for_unsupported_mode():
    # Create a mock Mode not present in our original Mode Enum
    class MockMode(Enum):
        WALKING = "WALKING"

    with pytest.raises(ValueError, match=r"Unsupported mode `WALKING`"):
        get_traveltime_specific_mode(MockMode.WALKING)
