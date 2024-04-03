from pathlib import Path

from e2slib.analysis import location

from weather.api import weather_api
from weather.structure import enums


def get_demo_location() -> location.GeoLocation:
  return location.GeoLocation("Demo_site", 52.414, -1.143, 90.6, 'UTC')


def get_weather_api_obj(loc: location.GeoLocation, simulation_year: int,
                        path_results: Path) -> weather_api.WeatherData:
  return weather_api.WeatherData(
      loc,
      simulation_year,
      weather_data_source=enums.WeatherDataSource.ERA5,
      saving_path=path_results)


def main() -> None:
  path_analysis_results = Path.cwd().parent / 'data'
  sim_year = 2020
  demo_loc = get_demo_location()
  demo_weather = get_weather_api_obj(demo_loc, sim_year, path_analysis_results)

  print(demo_weather.get_weather_data())


if __name__ == '__main__':
  main()
