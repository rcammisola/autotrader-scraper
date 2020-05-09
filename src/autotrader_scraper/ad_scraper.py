#!/usr/bin/python

# Will take a list of autotrader ad page IDs and scrape useful data from them,
# outputting in .csv format. The scraper function itself can be found in scraping.py

# Takes two arguments, in order:
# 1. an input file name (one line per ad url)
# 2. an output file name (appends by default)


import csv
import os
import sys

from autotrader_scraper import scraping

with open(str(sys.argv[1]), 'r') as i_file:  # url file
    url_list = i_file.readlines()

if os.path.isfile(sys.argv[2]):
    mode = 'a'
else:
    mode = 'w'

with open(str(sys.argv[2]), mode) as o_file:
    i = 0
    field_names = [
        'url', 'status_code', 'make', 'model', 'trim', 'manufactured_year',
        'condition', 'transmission', 'body_type', 'doors',
        'engine_size', 'seats', 'fuel_type', 'description', 'price',
        'townAndDistance', 'isTradeSeller', 'emailAddress', 'tax',
        'co2Emissions', 'mileage', 'raw_response'
    ]
    cwriter = csv.DictWriter(o_file, fieldnames=field_names)

    if mode == 'w':
        cwriter.writeheader()
    for url in url_list:
        row = scraping.ad_scraper(url)
        cwriter.writerow(row)
        i += 1
        if i % 10 == 0:
            print(i)

print('done')
