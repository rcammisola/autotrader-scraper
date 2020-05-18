#!/usr/bin/env python3

import argparse
from pathlib import Path
from typing import Text

import pandas as pd

from autotrader_scraper.advert import get_ads_from_search_results
from autotrader_scraper.search_results import SearchResults


def batch_scrape_ads_from_file_of_urls(file_of_urls: Text,
                                       output_file: Text) -> None:
    with open(file_of_urls) as f:
        base_search_urls = [line.strip() for line in f.readlines()]

    for i, base_search_url in enumerate(base_search_urls):
        print(f"##### URL {i+1}/{len(base_search_urls)}: {base_search_url}\n")
        scrape_ads_from_search_url(base_search_url, output_file)

    return


def scrape_ads_from_search_url(base_search_url: Text,
                               output_file: Text) -> None:
    output_file = Path(output_file).resolve()
    previous_ads = pd.read_parquet(str(output_file)) \
        if output_file.exists() else pd.DataFrame()

    search_results = SearchResults(base_url=base_search_url)
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
    parser.add_argument("-u", "--url",
                        required=False,
                        help="url of autotrader search page")
    parser.add_argument("-b", "--batch",
                        required=False,
                        help="path to file containing urls "
                             "of autotrader search pages (1 per line)"
                        )
    parser.add_argument("-o", "--output", help="path to output parquet file")
    args = parser.parse_args()
    if args.url:
        scrape_ads_from_search_url(base_search_url=args.url,
                                   output_file=args.output)
    else:
        assert args.batch, "Need to specify either --batch or --url arguments"
        batch_scrape_ads_from_file_of_urls(file_of_urls=args.batch,
                                           output_file=args.output)
