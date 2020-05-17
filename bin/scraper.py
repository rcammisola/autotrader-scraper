#!/usr/bin/env python3

import argparse
from pathlib import Path
from typing import Text

import pandas as pd

from autotrader_scraper.advert import get_ads_from_search_results
from autotrader_scraper.search_results import SearchResults


def main(base_url: Text, output_file: Text):
    output_file = Path(output_file).resolve()
    previous_ads = pd.read_parquet(str(output_file)) \
        if output_file.exists() else pd.DataFrame()

    search_results = SearchResults(base_url=base_url)
    ad_urls = search_results.get_pages()
    new_ads = get_ads_from_search_results(ad_urls, previous_ads)
    if len(new_ads) > 0:
        results = pd.concat([previous_ads, new_ads])
        print("Writing output")
        results.to_parquet(str(output_file))
    else:
        print("No new ads found")

    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", help="url of autotrader search page")
    parser.add_argument("-o", "--output", help="path to output file")
    args = parser.parse_args()
    main(base_url=args.url, output_file=args.output)
