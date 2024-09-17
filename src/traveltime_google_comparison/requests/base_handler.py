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
