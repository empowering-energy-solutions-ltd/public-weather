from enum import Enum, StrEnum, auto


class WeatherDataSource(StrEnum):
  TMY = auto()
  PVLIB_CLEARSKY = auto()
  ERA5 = auto()
  PVGISSARAH2 = auto()


class WeatherDataFormat(Enum):
  POA = auto(
  )  #based on direct, diffuse and total irradiance in the plane of array ('poa_global', 'poa_direct', 'poa_diffuse').
  DEFAULT = auto(
  )  #based on contains global horizontal, direct and diffuse horizontal irradiance ('ghi', 'dni' and 'dhi').


class ExtractFile(Enum):
  TEMPERATURE = "t2m", "2m_temperature"
  SOLARRADIATION = "ssr", "surface_net_solar_radiation"

  @property
  def filename_key(self) -> str:
    """Get the str which is used in naming the file."""
    return self.value[1]

  @property
  def column_name(self) -> str:
    """Get the column name related to the key."""
    return self.value[0]
