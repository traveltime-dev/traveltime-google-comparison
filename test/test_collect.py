import pytest
from datetime import datetime

import pytz
from traveltimepy import Coordinates

from traveltime_google_comparison.collect import (
    generate_time_instants,
    parse_coordinates,
    localize_datetime,
)


def test_generate_time_instants_with_time_window_divisible_by_interval():
    start = datetime(2023, 9, 5, 12, 0)
    end = datetime(2023, 9, 5, 14, 0)
    interval = 60
    result = generate_time_instants(start, end, interval)
    expected = [
        datetime(2023, 9, 5, 12, 0),
        datetime(2023, 9, 5, 13, 0),
        datetime(2023, 9, 5, 14, 0),
    ]
    assert result == expected


def test_generate_time_instants_when_time_window_is_smaller_than_interval():
    start = datetime(2023, 9, 5, 12, 0)
    end = datetime(2023, 9, 5, 12, 2)
    interval = 60
    result = generate_time_instants(start, end, interval)
    expected = [datetime(2023, 9, 5, 12, 0)]
    assert result == expected


def test_generate_time_instants_with_time_window_not_fully_divisible_by_interval():
    start = datetime(2023, 9, 5, 12, 0)
    end = datetime(2023, 9, 5, 14, 10)
    interval = 45
    result = generate_time_instants(start, end, interval)
    expected = [
        datetime(2023, 9, 5, 12, 0),
        datetime(2023, 9, 5, 12, 45),
        datetime(2023, 9, 5, 13, 30),
    ]
    assert result == expected


def test_generate_time_instants_with_end_time_before_start_raises_error():
    start = datetime(2023, 9, 5, 12, 0)
    end = datetime(2023, 9, 5, 11, 0)
    interval = 60
    with pytest.raises(ValueError):
        generate_time_instants(start, end, interval)


def test_parse_coordinates_simple_case():
    coord_str = "51.4614,-0.1120"
    assert parse_coordinates(coord_str) == Coordinates(lat=51.4614, lng=-0.1120)


def test_parse_coordinates_with_spaces():
    assert parse_coordinates("51.4614, -0.1120") == Coordinates(
        lat=51.4614, lng=-0.1120
    )
    assert parse_coordinates("51.4614 , -0.1120") == Coordinates(
        lat=51.4614, lng=-0.1120
    )
    assert parse_coordinates(" 51.4614 , -0.1120") == Coordinates(
        lat=51.4614, lng=-0.1120
    )
    assert parse_coordinates(" 51.4614 , -0.1120 ") == Coordinates(
        lat=51.4614, lng=-0.1120
    )


def test_parse_coordinates_missing_coma():
    with pytest.raises(ValueError):
        coord_str = "51.4614 -0.1120"
        parse_coordinates(coord_str)


def test_parse_coordinates_wrong_format():
    with pytest.raises(ValueError):
        coord_str = "51.4614,-0.1120,-122.4194"
        parse_coordinates(coord_str)


def test_basic_localize_datetime_with_UTC():
    date = "2023-09-13"
    time = "15:00"
    timezone = pytz.UTC
    result = localize_datetime(date, time, timezone)
    assert result == datetime(2023, 9, 13, 15, 0, tzinfo=pytz.UTC)


def test_localize_datetime_with_different_timezone():
    date = "2023-09-13"
    time = "15:00"
    timezone = pytz.timezone("US/Pacific")
    result = localize_datetime(date, time, timezone)
    expected_result = timezone.localize(datetime(2023, 9, 13, 15, 0))
    assert result == expected_result


def test_localize_datetime_with_incorrect_format():
    with pytest.raises(ValueError):
        wrong_date = "13-09-2023"
        time = "3:00"
        timezone = pytz.timezone("US/Pacific")
        localize_datetime(wrong_date, time, timezone)

    with pytest.raises(ValueError):
        date = "2023-09-13"
        wrong_time = "3:00 PM"
        timezone = pytz.timezone("US/Pacific")
        localize_datetime(date, wrong_time, timezone)
