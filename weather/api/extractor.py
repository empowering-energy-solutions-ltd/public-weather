import os
from dataclasses import dataclass, field
from pathlib import Path

import cdsapi
import pandas as pd
from dotenv import load_dotenv

from weather.api import functions
from weather.structure import enums, protocols

load_dotenv(override=True)


@dataclass
class Era5DataExtractor:
  """ Class to extract ERA5 data using CDS API. Make sure you've created and added your API keys to the .env file.
  Args: 
    location: protocols.Location
      Location object that holds the latitude and longitude of the location to extract the data.
    api_client: cdsapi.Client | None = None
      CDS API client to make the requests. If None, it will create a new client using the environment variables.
    saving_path: Path = Path(r'..')
      Path to save the netcdf files. Default is the parent directory.
    variables_to_extract: list[str] = field(default_factory=list)
      List of variables to extract. Default is empty, so it will extract all variables available.
      
    Methods:
    create_api_client:
      Create a new CDS API client using the environment variables.
    get_ghi_data:
      Get the GHI data from the extracted netcdf file.
    get_temperature_data:
      Get the temperature data from the extracted netcdf file.
    get_variable_file_path:
      Get the file path of the variable extracted.
    create_saving_path:
      Create the saving path to save the netcdf files.
    extract_multiple_year:
      Extract data from multiple years.
    all_monhts:
      Get all months in a list.
    get_box_coordinates:
      Get the box coordinates to extract the data.
    download_data:
      Download the data from the CDS API.
    """
  location: protocols.Location
  api_client: cdsapi.Client | None = None
  saving_path: Path = Path(r'..')
  variables_to_extract: list[str] = field(default_factory=list)

  def __post_init__(self) -> None:
    if self.api_client is None:
      self.create_api_client()
    self.variables_to_extract = [
        enums.ExtractFile.SOLARRADIATION.filename_key,
        enums.ExtractFile.TEMPERATURE.filename_key
    ]
    self.create_saving_path()

  def create_api_client(self):
    """Create a new CDS API client using the environment variables."""
    CDSAPI_URL = os.getenv('CDSAPI_URL')
    CDSAPI_KEY = '000'  #ßos.getenv('CDSAPI_KEY')
    try:
      self.api_client = cdsapi.Client(key=CDSAPI_KEY,
                                      url=CDSAPI_URL,
                                      verify=True)
    except AssertionError as e:
      print(f'Error: {e}')
    #   print(f'Error: {e}')

  def get_ghi_data(self, sim_year: int) -> pd.DataFrame:
    """Get the GHI data from the extracted netcdf file."""
    solar_era5_data_path = self.get_variable_file_path(
        enums.ExtractFile.SOLARRADIATION, sim_year)
    return functions.get_radiation_data(solar_era5_data_path)

  def get_temperature_data(self, sim_year: int) -> pd.DataFrame:
    """Get the temperature data from the extracted netcdf file."""
    temperature_era5_data_path = self.get_variable_file_path(
        enums.ExtractFile.TEMPERATURE, sim_year)
    temperature_data = functions.get_temperature_data(
        temperature_era5_data_path)
    return temperature_data

  def get_variable_file_path(self, variable: enums.ExtractFile,
                             year: int) -> Path:
    """Get the file path of the variable extracted."""
    filename = f'{self.location.name}_{variable.filename_key}_{year}.nc'
    print(self.saving_path / filename)
    return self.saving_path / filename

  def create_saving_path(self, saving_path: Path | None = None) -> None:
    """Create the saving path to save the netcdf files."""
    if saving_path is None:
      path_netcdf_files = self.saving_path / f'weather_data/{self.location.name}_netcdf_data'
    else:
      path_netcdf_files = saving_path / f'weather_data/{self.location.name}_netcdf_data'
    path_netcdf_files.mkdir(parents=True, exist_ok=True)
    self.saving_path = path_netcdf_files

  def extract_multiple_year(self):
    pass

  def all_monhts(self) -> list[str]:
    """Get all months in a list."""
    return [f'{x:02d}' for x in range(1, 13)]

  def get_box_coordinates(self) -> list[float]:
    """Get the box coordinates to extract the data."""
    box_coordinates = [self.location.latitude, self.location.longitude]
    box_coordinates = box_coordinates + [
        x - 0.01 if x > 0 else x + 0.01 for x in box_coordinates
    ]
    return box_coordinates

  def download_data(self, year: int, months: list[str] | None = None):
    """Download the data from the CDS API."""
    if months is None:
      months = self.all_monhts()

    for variable in self.variables_to_extract:
      filename = f'{self.location.name}_{variable}_{year}.nc'
      temp_full_path = self.saving_path / filename
      print(f'Check if {temp_full_path} already exists...')
      if not temp_full_path.exists():
        print('File does not exist')
        temp_result = self.api_client.retrieve(
            'reanalysis-era5-land', {
                'format':
                'netcdf',
                'variable':
                f'{variable}',
                'year':
                f'{year}',
                'month':
                months,
                'day': [
                    '01',
                    '02',
                    '03',
                    '04',
                    '05',
                    '06',
                    '07',
                    '08',
                    '09',
                    '10',
                    '11',
                    '12',
                    '13',
                    '14',
                    '15',
                    '16',
                    '17',
                    '18',
                    '19',
                    '20',
                    '21',
                    '22',
                    '23',
                    '24',
                    '25',
                    '26',
                    '27',
                    '28',
                    '29',
                    '30',
                    '31',
                ],
                'time': [
                    '00:00',
                    '01:00',
                    '02:00',
                    '03:00',
                    '04:00',
                    '05:00',
                    '06:00',
                    '07:00',
                    '08:00',
                    '09:00',
                    '10:00',
                    '11:00',
                    '12:00',
                    '13:00',
                    '14:00',
                    '15:00',
                    '16:00',
                    '17:00',
                    '18:00',
                    '19:00',
                    '20:00',
                    '21:00',
                    '22:00',
                    '23:00',
                ],
                'area':
                self.get_box_coordinates(),
            }, f'{temp_full_path}')
      else:
        print(f'{temp_full_path} already exists.')
