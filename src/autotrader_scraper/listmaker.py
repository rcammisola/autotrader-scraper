# Listmaker
# Usage:
# ./listmaker.py https://www.autotrader.co.uk/car-search?advert... url_list.txt
# if file exists, we append

import os
import sys

from autotrader_scraper import scraping

base_url = sys.argv[1]
out_fname = sys.argv[2]

if not os.path.isfile(out_fname):
    z = open(out_fname, 'w')
    z.close()

page_count = 1
while True:
    url = f"{base_url}&page={page_count}"
    results = scraping.search_result_scraper(url)
    if len(results) > 0:
        with open(out_fname, 'a') as fcon:
            for r in results:
                fcon.write('https://www.autotrader.co.uk' + r)
                fcon.write('\n')
        page_count += 1
        print(page_count)
        print(len(results))
    else:
        break
