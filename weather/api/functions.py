from pathlib import Path

import pandas as pd
import xarray as xr

from weather.structure import enums, schema


def get_weather_data_format(
    weather_data_columns: list[str]) -> enums.WeatherDataFormat:
  """Get the weather data format from the columns of the dataframe."""
  weather_data_format = enums.WeatherDataFormat.DEFAULT
  if 'poa_global' in weather_data_columns:
    weather_data_format = enums.WeatherDataFormat.POA

  return weather_data_format


def apply_outputdataschema(dataf: pd.DataFrame,
                           target_variable: enums.ExtractFile) -> pd.DataFrame:
  """Apply the output data schema to the dataframe."""
  if target_variable is enums.ExtractFile.TEMPERATURE:
    dataf.index.name = schema.WeatherDataSchema.DATEINDEX
    dataf.columns = [schema.WeatherDataSchema.OAT]
  elif target_variable is enums.ExtractFile.SOLARRADIATION:
    dataf.index.name = schema.WeatherDataSchema.DATEINDEX
    dataf.columns = [schema.WeatherDataSchema.SOLARIRRADIANCE]
  else:
    print(f'Schema not recognized for target variable: {target_variable}')
  return dataf


def get_all_data(target_area: str) -> pd.DataFrame:
  """Get all the data from the netcdf files."""
  frames = []
  functions = [get_radiation_data, get_temperature_data]
  for f in functions:
    frames.append(f(target_area))

  return pd.concat(frames, axis=1)


def get_radiation_data(path_netcdf_file: Path) -> pd.DataFrame:
  """ Retrieve solar radiation data from the extracted netcdf file."""
  target_variable = enums.ExtractFile.SOLARRADIATION
  print(path_netcdf_file)

  if path_netcdf_file.exists():
    # Load data
    radiation_data = load_single_netcdf_file(path_netcdf_file, target_variable)
    radiation_data = radiation_data - radiation_data.shift()
    radiation_data.fillna(0, inplace=True)
    radiation_data[radiation_data < 0] = 0
    radiation_data[target_variable.column_name] = (
        radiation_data[target_variable.column_name] / 3600
    )  # convert from J/m2 to W/m2
  else:
    radiation_data = pd.DataFrame(columns=[target_variable.column_name])

  return apply_outputdataschema(radiation_data, target_variable)


def get_temperature_data(path_netcdf_file: Path) -> pd.DataFrame:
  """Get the temperature data from the extracted netcdf file."""
  target_variable = enums.ExtractFile.TEMPERATURE
  if path_netcdf_file.exists():
    print("file exists")
    temperature_data = load_single_netcdf_file(path_netcdf_file,
                                               target_variable)
    temperature_data[target_variable.column_name] = (
        temperature_data[target_variable.column_name] - 273.15
    )  # convert from degreeK to degreeC
  else:
    temperature_data = pd.DataFrame(columns=[target_variable.column_name])
  return apply_outputdataschema(temperature_data, target_variable)


def load_single_netcdf_file(
    path_netcdf_file: Path,
    target_variable: enums.ExtractFile) -> pd.DataFrame:
  """Load a single netcdf file and transform it into a dataframe."""
  temp_xarray = xr.open_dataset(path_netcdf_file)
  temp_dataf = temp_xarray.to_dataframe()

  temp_dataf = temp_dataf.reset_index()
  if 'expver' in temp_dataf.columns:
    filt = temp_dataf['expver'] == 1
    df1 = temp_dataf.loc[filt, ['time', target_variable.column_name]].copy()
    df1.set_index('time', inplace=True)
    filt = temp_dataf['expver'] == 5
    df2 = temp_dataf.loc[filt, ['time', target_variable.column_name]].copy()
    df2.set_index('time', inplace=True)
    temp_dataf = df1.combine_first(df2)

  else:
    temp_dataf = temp_dataf[['time', target_variable.column_name]]
    temp_dataf = temp_dataf.set_index('time', drop=True)
  temp_dataf.index = temp_dataf.index.tz_localize('UTC')
  return temp_dataf


def load_netcdf_files(path_directory: Path,
                      target_variable: enums.ExtractFile) -> pd.DataFrame:
  """Load netcdf file and transform them into dataframes."""
  pathlist = path_directory.rglob('*.nc')
  frames: list[pd.DataFrame] = []
  for path in pathlist:
    if target_variable.filename_key in path.stem:
      temp_xarray = xr.open_dataset(path)
      temp_dataf = temp_xarray.to_dataframe()
      temp_dataf = temp_dataf.unstack([0, 1]).iloc[:, 0]
      temp_dataf = temp_dataf.to_frame()
      temp_dataf.columns = temp_dataf.columns.get_level_values(0)
      frames.append(temp_dataf)
  if len(frames) > 0:
    concat_dataf = pd.concat(frames)
    concat_dataf.index = concat_dataf.index.tz_localize('utc')
  else:
    concat_dataf = pd.DataFrame(columns=[target_variable.column_name])
  return concat_dataf
