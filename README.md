weather_api
==============================

The weather package is used to call weather apis and gather weather and solar irradiance data. This tool is primarily helpful with running the solar PV feature to estimate the annual solar irradiance that a site may receive.

Before running the functions you will need to create a era5 account an generate an API key. See the details about how to create an account and install cd api at: https://cds.climate.copernicus.eu/api-how-to. The url and token will then need to be added to the `.env` file so that the tools functions can call the needed APIs.



Project Organization
------------

    ├── LICENSE
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── Demo_site_netcdf_data      <- Saved example output data from the API
    │   │   ├── Demo_site_2m_temperature_2020.nc 
    │   │   ├── Demo_site_surface_net_solar_radiation_2020.nc
    │   │   └── Demo_site_surface_net_solar_radiation_2022.nc
    │   └── Weather_data_era5_2020.csv            <- ERA5 data example
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │   └── Demo_notebook.ipynb       <- Demo notebook to show package functions
    │
    ├── weather                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── api           <- Scripts to download or generate data
    │   │   ├── extractor.py      <- Script holding the data extractor for the ERA5 weather data API.
    │   │   ├── functions.py      <- Script holding functions for data retrieval and loading.
    │   │   └── weather_api.py      <- Script holding WeatherData class for calling the weather APIs and returning formatted data.
    │   │
    │   ├── structure       <- Scripts for structuring the project in a uniform manner
    │   │   ├── enums.py    <- Enums script for project
    │   │   ├── protocols.py   <- Script holding necessary protocols for the project
    │   │   └── schema.py   <- Schemas for the project
    │   │
    │   └── main.py  <- Main script. Used to run a demonstration of the project functions.
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │
    ├── pyproject.toml   <- The .toml file for poetry venv creation.
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
