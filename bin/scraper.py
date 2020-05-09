import argparse
from typing import Text

from autotrader_scraper.advert import Advert
from autotrader_scraper.search_results import SearchResults


def main(base_url: Text):
    search_results = SearchResults(base_url=base_url, max_results=20)
    ads = [Advert(url) for url in search_results.pages]
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="url of autotrader search page")
    args = parser.parse_args()
    main(base_url=args.url)
