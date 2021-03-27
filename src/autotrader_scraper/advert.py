import collections
import json
import re
from typing import Text, Dict, Union, Mapping, List


from pprint import pprint

import pandas as pd
import requests

from tqdm import tqdm

URL = Text
AtomicTypes = Union[int, float, Text, bool]
AD_ID_PATTERN = r'([0-9]{15})'


def get_ad_id_from_url(url: URL) -> Text:
    return re.search(AD_ID_PATTERN, url)[0]


def get_ads_from_search_results(ad_urls: List[URL],
                                previous_ads: pd.DataFrame) -> pd.DataFrame:
    results = pd.DataFrame()
    for url in tqdm(ad_urls):
        try:
            ad_id = get_ad_id_from_url(url)
            if ad_id in previous_ads.index:
                continue
            ad = Advert(url)
            df = pd.DataFrame(data=[ad.contents], index=[ad_id])
            results = pd.concat([results, df])
        except ValueError as ve:
            print(f"ERROR: {ve}")
    print(f"Scraped {len(results)} new ads")
    return results


class Advert:
    def __init__(self, url: URL):
        self.url = url
        self.id = get_ad_id_from_url(url)
        self._contents = None
        self.base_url = 'https://www.autotrader.co.uk/json/fpa/initial/'

    def __repr__(self):
        return json.dumps(self.contents)

    @property
    def contents(self):
        if not self._contents:
            self._contents = self.scrape()
        return self._contents

    def scrape(self) -> Dict[Text, AtomicTypes]:
        url_id = re.findall('[0-9]{11,}', self.url)[0]
        request_url = f"{self.base_url}{url_id}"

        nested_properties = self.make_request(request_url)

        flattened_properties = flatten_dict(nested_properties)

        keys_to_drop = [
            "advert_imageUrls",
            "advert_images",
            "pageData_metadata"
        ]
        for key in keys_to_drop:
            flattened_properties.pop(key)

        id_from_page = flattened_properties["pageData_tracking_ad_id"]
        msg = f"ID on page ({id_from_page}) didn't match ID in URL ({self.id})"
        assert id_from_page == self.id, msg

        flattened_properties.update(
            self.scrape_vehicle_technical_specs(flattened_properties["vehicle_derivativeId"])
        )

        return flattened_properties

    def scrape_vehicle_technical_specs(self, derivative_id):
        technical_spec_url = f"https://www.autotrader.co.uk/json/taxonomy/technical-specification?derivative={derivative_id}"
        result_dict = self.make_request(technical_spec_url)

        performance_specs = [specs["specs"] for specs in result_dict["techSpecs"] if specs["specName"] == "Economy & performance"]
        dimension_specs = [specs["specs"] for specs in result_dict["techSpecs"] if specs["specName"] == "Dimensions"]

        technical_specs = {}
        technical_specs.update(
            {s["name"]: s["value"] for s in performance_specs[0]}
        )
        technical_specs.update(
            {s["name"]: s["value"] for s in dimension_specs[0]}
        )

        return technical_specs

    def make_request(self, request_url):
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        response = requests.get(request_url, timeout=5, headers=headers)

        if response.status_code != 200:
            raise ValueError(f"Unable to retrieve ad from: {request_url}")

        return json.loads(response.content.decode('utf-8'))


def flatten_dict(d: Mapping,
                 parent_key: Text = '',
                 sep: Text = '_') -> Dict[Text, AtomicTypes]:
    """ From https://stackoverflow.com/a/6027615 """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
