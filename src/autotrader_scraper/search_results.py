from typing import Text, List

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
        self._pages = None

    @property
    def pages(self) -> List[URL]:
        if self._pages:
            return self._pages

        results = []
        page_count = 1
        while True:
            url = f"{self.base_url}&page={page_count}"
            urls_from_page = self.scrape(url)
            results += urls_from_page

            if len(results) > self.max_results or page_count > self.max_pages:
                break
            elif len(urls_from_page) == 0:
                break
            else:
                page_count += 1

        self._pages = results[:self.max_results]
        return self._pages

    @staticmethod
    def scrape(url: Text) -> List[URL]:
        response = requests.get(url, timeout=5)
        tree = html.fromstring(response.content.decode('utf-8'))
        res = set(
            tree.xpath('//a[contains(@class, "listing-fpa-link")]/@href'))
        return list(res)
