[![Build Status](https://travis-ci.com/musab-k/autotrader-scraper.svg?branch=master)](https://travis-ci.com/musab-k/autotrader-scraper)

# autotrader-scraper
Autotrader.co.uk data scraper.

Forked from [liudvikasakelis/autotrader-scraper](https://github.com/liudvikasakelis/autotrader-scraper).

# Usage

Install dependencies using [poetry](https://github.com/python-poetry/poetry)
```shell script
poetry install
```

Go to autotrader.co.uk, perform a search and copy the url. To run the script:
```shell script
poetry run bin/scraper.py "$SEARCH_URL" "$PATH_TO_OUTPUTS_CSV"
```
