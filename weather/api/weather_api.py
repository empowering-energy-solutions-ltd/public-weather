from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import pvlib
from e2slib.utillib import functions as e2s_functions

from weather.api import extractor
from weather.structure import enums, protocols, schema


@dataclass
class WeatherData:
  """Class to handle weather data from different sources.
  Args:
    geolocation: protocols.Location
      Location of the site.
    simulation_year: int
      Year of the simulation.
    weather_data_source: enums.WeatherDataSource
      Source of the weather data.
    saving_path: Path
      Path to save the weather data.
  
  Methods:
    start_date() -> pd.Timestamp
      Get the start date of the simulation year.
    end_date() -> pd.Timestamp
      Get the end date of the simulation year.
    location() -> pvlib.location.Location
      Get the location of the site.
    get_weather_data_source() -> enums.WeatherDataSource
      Get the weather data source.
    convert_to_poa(dataf: pd.DataFrame) -> pd.DataFrame
      Convert a dataframe with dni, ghi, dhi, apparent_zenith, azimuth and airmass_relative to poa.
    get_clearsky_solar_data() -> pd.DataFrame
      Get the clearsky solar data.
    get_tmy_weather_data() -> pd.DataFrame
      Get the TMY weather data.
    get_sarah2_weather_data() -> pd.DataFrame
      Get the SARAH2 weather data.
    format_sarah_weather_data(dataf: pd.DataFrame) -> pd.DataFrame
      Format the SARAH2 weather data.
    get_weather_data_from_era5() -> pd.DataFrame
      Get the weather data from ERA5.
    add_solar_components_to_ghi_data(ghi_data: pd.DataFrame) -> pd.DataFrame
      Add solar components to the GHI data.
    get_date_range() -> pd.DatetimeIndex
      Get the date range of the simulation year.
    weather_data_processing(dataf: pd.DataFrame) -> pd.DataFrame
      Resample and fill missing data.
    get_weather_data(weather_data_source: enums.WeatherDataSource | None = None) -> pd.DataFrame
      Get the weather data.
    save_weather_data(dataf: pd.DataFrame) -> None
      Save the weather data."""
  geolocation: protocols.Location
  simulation_year: int
  weather_data_source: enums.WeatherDataSource = enums.WeatherDataSource.ERA5
  saving_path: Path = Path(r'..')

  def __post_init__(self):
    print(f"The results will be stored at:\n{self.saving_path.resolve()}")

  @property
  def start_date(self) -> pd.Timestamp:
    return pd.Timestamp(f'{self.simulation_year}-01-01')

  @property
  def end_date(self) -> pd.Timestamp:
    return pd.Timestamp(f'{self.simulation_year}-12-31 23:30:00')

  @property
  def location(self) -> pvlib.location.Location:
    return pvlib.location.Location(self.geolocation.latitude,
                                   self.geolocation.longitude)

  def get_weather_data_source(self) -> enums.WeatherDataSource:
    """Get the weather data source."""
    return self.weather_data_source

  def convert_to_poa(self, dataf: pd.DataFrame) -> pd.DataFrame:
    """Convert a dataframe with dni, ghi, dhi, apparent_zenith, azimuth and airmass_relative to poa"""

    # Calculate solar position for each timestamp in weather_data data
    solar_position = self.location.get_solarposition(dataf.index)

    # Calculate airmass for each timestamp in weather_data data
    airmass = self.location.get_airmass(dataf.index)

    # Calculate POA irradiance for each timestamp in weather_data data
    dataf = pvlib.irradiance.get_total_irradiance(
        surface_tilt=0,
        surface_azimuth=180,
        solar_zenith=solar_position['apparent_zenith'],
        solar_azimuth=solar_position['azimuth'],
        dni=dataf['dni'],
        ghi=dataf['ghi'],
        dhi=dataf['dhi'],
        airmass=airmass['airmass_relative'])
    return dataf

  def get_clearsky_solar_data(self) -> pd.DataFrame:
    """ Get data from the clearsky api """
    # Define location using latitude and longitude
    # Generate a range of timestamps for the desired date range and frequency
    date_range = self.get_date_range()

    # Load weather_data data for location
    solar_data: pd.DataFrame = self.location.get_clearsky(date_range)

    return self.convert_to_poa(solar_data)

  def get_tmy_weather_data(self) -> pd.DataFrame:
    weather_data = pvlib.iotools.get_pvgis_tmy(self.geolocation.latitude,
                                               self.geolocation.longitude,
                                               map_variables=True)[0]
    weather_data.index.name = schema.POAWeatherDataSchema.INDEX
    return weather_data

  def get_sarah2_weather_data(self) -> pd.DataFrame:
    """ Get data from the SARAH2 api"""
    weather_data = pvlib.iotools.get_pvgis_hourly(
        latitude=self.geolocation.latitude,
        longitude=self.geolocation.longitude,
        start=self.start_date,
        end=self.end_date,
        raddatabase='PVGIS-SARAH2',
        url='https://re.jrc.ec.europa.eu/api/v5_2/')[0]

    weather_data = self.format_sarah_weather_data(weather_data)
    return weather_data

  def format_sarah_weather_data(self, dataf: pd.DataFrame) -> pd.DataFrame:
    """Format the SARAH2 weather data."""
    poa_global_cols = [
        schema.POAWeatherDataSchema.POA_DIRECT,
        schema.POAWeatherDataSchema.POA_GROUND_DIFFUSE,
        schema.POAWeatherDataSchema.POA_SKY_DIFFUSE
    ]
    dataf[schema.POAWeatherDataSchema.POA_GLOBAL] = dataf[poa_global_cols].sum(
        axis=1)

    poa_diffuse_cols = [
        schema.POAWeatherDataSchema.POA_GROUND_DIFFUSE,
        schema.POAWeatherDataSchema.POA_SKY_DIFFUSE
    ]
    dataf[schema.POAWeatherDataSchema.
          POA_DIFFUSE] = dataf[poa_diffuse_cols].sum(axis=1)
    dataf.index.name = schema.POAWeatherDataSchema.INDEX
    dataf.index = dataf.index.tz_convert(self.geolocation.timezone)
    return dataf

  def get_weather_data_from_era5(self) -> pd.DataFrame:
    """Get the weather data from ERA5 api."""
    site_era5_extractor = extractor.Era5DataExtractor(
        self.geolocation, saving_path=self.saving_path)
    site_era5_extractor.download_data(self.simulation_year)

    ghi_data = site_era5_extractor.get_ghi_data(self.simulation_year)
    weather_data = self.add_solar_components_to_ghi_data(ghi_data).copy()
    temperature_data = site_era5_extractor.get_temperature_data(
        self.simulation_year)
    weather_data.loc[:, schema.POAWeatherDataSchema.
                     OUTDOOR_AIR_TEMPERATURE] = temperature_data.values.flatten(
                     )
    return weather_data

  def add_solar_components_to_ghi_data(self,
                                       ghi_data: pd.DataFrame) -> pd.DataFrame:
    """Add solar components to the GHI data."""
    ghi_data.columns = ['ghi']
    # Calculate solar position for each timestamp in weather_data data
    solar_position: pd.DataFrame = self.location.get_solarposition(
        ghi_data.index)
    dni_data: pd.DataFrame = pvlib.irradiance.disc(
        ghi_data['ghi'].values,
        solar_zenith=solar_position['zenith'],
        datetime_or_doy=ghi_data.index)
    weather_data: pd.DataFrame = pd.concat([dni_data, ghi_data], axis=1)
    # weather_data = pd.concat([weather_data, temperature_data], axis=1)
    weather_data['dhi'] = (
        weather_data['ghi'] -
        np.cos(solar_position['zenith'] * np.pi / 180) * weather_data['dni']
    )  # GHI = DNI*cosθ + DHI
    return self.convert_to_poa(weather_data)

  def get_date_range(self) -> pd.DatetimeIndex:
    """Get the date range of the simulation year."""
    return pd.date_range(start=self.start_date,
                         end=self.end_date,
                         freq='30min',
                         tz=self.geolocation.timezone)

  def weather_data_processing(self, dataf: pd.DataFrame) -> pd.DataFrame:
    """Resample and fill missing data."""
    date_range = self.get_date_range()
    dataf = e2s_functions.resample_and_fill_missing_data(dataf, freq="30min")
    dataf = pd.concat([pd.DataFrame(index=date_range), dataf], axis=1)
    return e2s_functions.fill_missing_data(dataf)

  def get_weather_data(
      self,
      weather_data_source: enums.WeatherDataSource | None = None
  ) -> pd.DataFrame:
    """Get the weather data."""
    weather_func_dict = {
        enums.WeatherDataSource.PVLIB_CLEARSKY: self.get_clearsky_solar_data,
        enums.WeatherDataSource.ERA5: self.get_weather_data_from_era5,
        enums.WeatherDataSource.PVGISSARAH2: self.get_sarah2_weather_data,
        enums.WeatherDataSource.TMY: self.get_tmy_weather_data,
    }
    if weather_data_source is None:
      weather_data_source = self.weather_data_source
    print(weather_data_source)
    weather_func = weather_func_dict.get(weather_data_source,
                                         self.get_tmy_weather_data)
    dataf = weather_func()
    dataf = self.weather_data_processing(dataf)
    self.save_weather_data(dataf)
    return dataf

  def save_weather_data(self, dataf: pd.DataFrame) -> None:
    """Save the weather data."""
    filename = f'Weather_data_{self.weather_data_source.name.lower()}_{self.simulation_year}.csv'
    path_saving_weather_data = self.saving_path / 'weather_data'

    path_saving_weather_data.mkdir(parents=True, exist_ok=True)
    dataf.to_csv(path_saving_weather_data / f'{filename}')
