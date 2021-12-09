# Interactive Covid Dashboard - Python

Interactive Covid Dashboard is a python program that displays live coronavirus data from the UK and news articles.
The Dashboard allows for scheduling manual updates as well as automatic updates for both news and covid data.
Articles can be removed and removed articles will not be seen again until the program is rebooted.
Scheduled events can be cancelled, with the event being removed from the scheduler.


## Installation

To install, download and unzip the repository to your desired location.

## Running

To run the dashboard double click the 'main.py' file.

*Requires python 3.7+ to be installed.

## Usage

The Dashboard allows for scheduling manual updates as well as automatic updates for both news and covid data.

Articles can be removed and removed articles will not be seen again until the program is rebooted.

Scheduled events can be cancelled, with the event being removed from the scheduler.

## Configuration

This program includes a config.json file which can be used to alter the program. "data" refers to the parameters for the uk-covid19 API, valid parameters can be found [here](https://coronavirus.data.gov.uk/details/developers-guide/main-api#query-parameters). "interval" being the time between automated updates.

```json

"data": 
    {
        "AreaName": "Exeter",
        "AreaType": "ltla",
        "NationName": "England",
        "interval": 300
    }
```

"news" refers to the parameters used for the NewsAPI, valid parameters can be found [here](https://newsapi.org/docs). "interval" being the time between automated updates.

```json

"news": 
    {
        "keywords":"covid coronavirus COVID-19",
        "language": "en",
        "sortBy":"publishedAt",
        "api key": "9276ffd05cb4487980d806b50a365674",
        "interval": 1200
    }
```

The favicon for the webpage can also be changed, it must be a  16x16 image.

```
"favicon":"https://icons.iconarchive.com/icons/avosoft/warm-toolbar/16/world-icon.png"
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
