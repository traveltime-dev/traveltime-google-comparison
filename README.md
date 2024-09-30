# TravelTime/Google comparison tool

This tool compares the travel times obtained from [TravelTime Routes API](https://docs.traveltime.com/api/reference/routes),
[Google Maps Directions API](https://developers.google.com/maps/documentation/directions/get-directions),
[TomTom Routing API](https://developer.tomtom.com/routing-api/documentation/tomtom-maps/routing-service),
[HERE Routing API](https://www.here.com/docs/bundle/routing-api-v8-api-reference),
[Mapbox Directions API](https://docs.mapbox.com/api/navigation/directions/),
[OpenRoutes API](https://openrouteservice.org/dev/#/api-docs/v2/directions/%7Bprofile%7D/get),
and [OSRM Routes API](https://project-osrm.org/docs/v5.5.1/api/?language=cURL#route-service).
Source code is available on [GitHub](https://github.com/traveltime-dev/traveltime-google-comparison).

## Features

- Get travel times from TravelTime API, Google Maps API, TomTom API, HERE API, Mapbox API and OSRM API in parallel, for provided origin/destination pairs and a set 
    of departure times.
- Departure times are calculated based on user provided start time, end time and interval.  
- Analyze the differences between the results and print out the average error percentage.

## Prerequisites

The tool requires Python 3.8+ installed on your system. You can download it from [here](https://www.python.org/downloads/).

## Installation
Create a new virtual environment with a chosen name (here, we'll name it 'env'):
```bash
python -m venv env
```

Activate the virtual environment:
```bash
source env/bin/activate
```

Install the project and its dependencies:
```bash
pip install traveltime-google-comparison
```

## Setup
Provide credentials and desired max requests per minute for the APIs inside the `config.json` file.
You can also disable unwanted APIs by changing the `enabled` value to `false`.

```json
{
  "traveltime": {
    "app-id": "<your-app-id>",
    "api-key": "<your-api-key>",
    "max-rpm": "60"
  },
  "api-providers": [
    {
      "name": "google",
      "enabled": true,
      "api-key": "<your-api-key>",
      "max-rpm": "60"
    },
    ...other providers
  ]
}
```

## Usage
Run the tool:
```bash
traveltime_google_comparison --input [Input CSV file path] --output [Output CSV file path] \
    --date [Date (YYYY-MM-DD)] --start-time [Start time (HH:MM)] --end-time [End time (HH:MM)] \
    --interval [Interval in minutes] --time-zone-id [Time zone ID] 
```
Required arguments:
- `--input [Input CSV file path]`: Path to the input file. Input file is required to have a header row and at least one 
    row with data, with two columns: `origin` and `destination`.
    The values in the columns must be latitude and longitude pairs, separated 
    by comma and enclosed in double quotes. For example: `"51.5074,-0.1278"`. Columns must be separated by comma as well.
    Check out the [project's repository](https://github.com/traveltime-dev/traveltime-google-comparison.git) 
    for examples in the `examples` directory and more pre-prepared routes in the `inputs` directory.
- `--output [Output CSV file path]`: Path to the output file. It will contain the gathered travel times. 
  See the details in the [Output section](#output)
- `--date [Date (YYYY-MM-DD)]`: date on which the travel times are gathered. Use a future date, as Google API returns
  errors for past dates (and times). Take into account the time needed to collect the data for provided input.
- `--start-time [Start time (HH:MM)]`: start time in `HH:MM` format, used for calculation of departure times.
  See [Calculating departure times](#calculating-departure-times)
- `--end-time [End time (HH:MM)]`: end time in `HH:MM` format, used for calculation of departure times.
  See [Calculating departure times](#calculating-departure-times)
- `--interval [Interval in minutes]`: interval in minutes, used for calculation of departure times. 
   See [Calculating departure times](#calculating-departure-times)
- `--time-zone-id [Time zone ID]`: non-abbreviated time zone identifier in which the time values are specified. 
  For example: `Europe/London`. For more information, see [here](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

Optional arguments:
- `--config [Config file path]`: Path to the config file. Default - ./config.json

Example:

```bash
traveltime_google_comparison --input examples/uk.csv --output output.csv --date 2023-09-20 \
    --start-time 07:00 --end-time 20:00 --interval 180 --time-zone-id "Europe/London"
```

## Calculating departure times
Script will collect travel times on the given day for departure times between provided start-time and end-time, with the
given interval. The start-time and end-time are in principle inclusive, however if the time window is not exactly divisible by the 
given interval, the end-time will not be included. For example, if you set the start-time to 08:00, end-time to 20:00 
and interval to 240, the script will sample both APIs for departure times 08:00, 12:00, 16:00 and 20:00 (end-time 
included). But for interval equal to 300, the script will sample APIs for departure times 08:00, 13:00 and 18:00 (end-time 
is not included).

## Output
The output file will contain the `origin` and `destination` columns from input file, with additional 4 columns: 
  - `departure_time`: departure time in `YYYY-MM-DD HH:MM:SS±HHMM` format, calculated from the start-time, end-time and interval.
    It includes date, time and timezone offset.
  - `google_travel_time`: travel time gathered from Google Directions API in seconds
  - `tt_travel_time`: travel time gathered from TravelTime API in seconds
  - `error_percentage_*`: relative error between provider and TravelTime travel times in percent, relative to provider result.

### Sample output
```csv
origin,destination,departure_time,google_travel_time,tomtom_travel_time,here_travel_time,osrm_travel_time,openroutes_travel_time,mapbox_travel_time,tt_travel_time,error_percentage_google,error_percentage_tomtom,error_percentage_here,error_percentage_mapbox,error_percentage_osrm,error_percentage_openroutes
"52.200400622501455, 0.1082577055247136","52.21614536733819, 0.15782831362961777",2024-09-25 07:00:00+0100,621.0,805.0,614.0,532.0,697.0,1018.0,956.0,53,18,55,6,79,37
```

## License
This project is licensed under MIT License. For more details, see the LICENSE file.
