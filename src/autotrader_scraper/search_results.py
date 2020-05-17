from typing import Text, List

import numpy as np
import requests
from lxml import html

URL = Text


class SearchResults:
    def __init__(self, base_url: Text,
                 max_results: int = 1000,
                 max_pages: int = 200):
        self.base_url = base_url
        self.max_results = max_results
        self.max_pages = max_pages

    def get_pages(self) -> List[URL]:
        all_ad_urls = []
        page_count = 1
        print("Scraping search pages for ads...")
        while True:
            search_url = f"{self.base_url}&page={page_count}"
            ad_urls = self.scrape_urls_from_page(search_url)

            if all([url in all_ad_urls for url in ad_urls]):
                # page=n will auto revert to n=1 if n>number of results pages
                # so check for duplicates and stop early
                break

            all_ad_urls += ad_urls

            if len(all_ad_urls) > self.max_results:
                break
            elif page_count > self.max_pages:
                break
            elif len(ad_urls) == 0:
                break

            page_count += 1

        print(f"Found {len(ad_urls)} ad URLs "
              f"from {page_count} search pages")
        return list(np.unique(all_ad_urls[:self.max_results]))

    @staticmethod
    def scrape_urls_from_page(url: Text) -> List[URL]:
        response = requests.get(url, timeout=5)
        tree = html.fromstring(response.content.decode('utf-8'))
        res = set(
            tree.xpath('//a[contains(@class, "listing-fpa-link")]/@href'))
        return list(res)
