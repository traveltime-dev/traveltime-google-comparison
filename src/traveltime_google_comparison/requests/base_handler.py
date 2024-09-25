from abc import ABC, abstractmethod
from dataclasses import dataclass

from datetime import datetime
from typing import Optional

from aiolimiter import AsyncLimiter
from traveltimepy import Coordinates

from traveltime_google_comparison.config import Mode


@dataclass
class RequestResult:
    travel_time: Optional[int]


class BaseRequestHandler(ABC):
    _rate_limiter: AsyncLimiter
    _just_checking_if_it_complains: str

    @abstractmethod
    async def send_request(
        self,
        origin: Coordinates,
        destination: Coordinates,
        departure_time: datetime,
        mode: Mode,
    ) -> RequestResult:
        pass

    @property
    def rate_limiter(self) -> AsyncLimiter:
        return self._rate_limiter


def create_async_limiter(max_rpm: int) -> AsyncLimiter:
    # Convert max_rpm to requests per second
    rps = max_rpm / 60

    if rps < 1:
        # For rates less than 1 per second, we'll use a longer time period
        # to allow fractional rates, but keep max_rate low to prevent bursts
        time_period = min(60, 1 / rps)
        max_rate = rps * time_period
    else:
        # For rates of 1 per second or higher, use a 1-second time period
        time_period = 1
        max_rate = rps

    return AsyncLimiter(max_rate=max_rate, time_period=time_period)
