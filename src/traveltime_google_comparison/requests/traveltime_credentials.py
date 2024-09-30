from dataclasses import dataclass
from typing import Optional


@dataclass
class Credentials:
    api_key: str
    app_id: Optional[str] = None
