#!/usr/bin/env python3

import argparse
from pathlib import Path
from typing import Text

import pandas as pd

from autotrader_scraper.advert import Advert
from autotrader_scraper.search_results import SearchResults


def main(base_url: Text, output_file: Text):
    search_results = SearchResults(base_url=base_url)
    ads = []
    n_pages = len(search_results.pages)
    for i, url in enumerate(search_results.pages):
        ads.append(Advert(url))
        if i % 10 == 0:
            print(f"Scraping ad {i} / {n_pages}")
    df = pd.DataFrame(data=[ad.contents for ad in ads],
                      index=[ad.url for ad in ads])
    output_file = str(Path(output_file).resolve())
    print("Writing csv")
    df.to_csv(output_file)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="url of autotrader search page")
    parser.add_argument("file", help="path to output csv file")
    args = parser.parse_args()
    main(base_url=args.url, output_file=args.file)
