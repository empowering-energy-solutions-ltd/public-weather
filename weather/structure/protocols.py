from dataclasses import dataclass
from typing import Protocol


@dataclass
class Location(Protocol):
  name: str
  latitude: float
  longitude: float
  altitude: float
  timezone: str