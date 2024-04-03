class WeatherDataSchema:
  DATEINDEX = 'Time'
  SOLARIRRADIANCE = 'Global irradiance (W/m2)'
  WINDSPEED = 'Wind speed (m/s) '
  OAT = 'Air temperature (deg C)'


class PVlibWeatherDataSchema:
  DNI = 'dni'
  GHI = 'ghi'
  DHI = 'dhi'
  OUTDOOR_AIR_TEMPERATURE = 'temp_air'
  CELL_TEMPERATURE = 'cell_temperature'
  MODULE_TEMPERATURE = 'module_temperature'
  WIND_SPEED = 'wind_speed'
  ALBEDO = 'albedo'


class POAWeatherDataSchema:
  INDEX = 'utc_time'
  POA_GLOBAL = 'poa_global'  #Global irradiance on inclined plane (W/m^2)
  POA_DIFFUSE = 'poa_diffuse'
  POA_DIRECT = 'poa_direct'  #Beam (direct) irradiance on inclined plane (W/m^2)
  POA_SKY_DIFFUSE = 'poa_sky_diffuse'  #Diffuse irradiance on inclined plane (W/m^2)
  POA_GROUND_DIFFUSE = 'poa_ground_diffuse'  #Reflected irradiance on inclined plane (W/m^2)
  SOLAR_ELEVATION = 'solar_elevation'  #Sun height/elevation (degrees)
  OUTDOOR_AIR_TEMPERATURE = 'temp_air'  #Air temperature at 2 m (degrees Celsius)
  WIND_SPEED = 'wind_speed'  #Wind speed at 10 m (m/s)
  SOLAR_RADIATION_RECONSTRUCTED = 'Int'  #Solar radiation reconstructed (1/0)
