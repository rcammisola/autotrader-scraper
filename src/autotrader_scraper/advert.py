import collections
import json
import re
from typing import Text, Dict, Union, Mapping, List

import pandas as pd
import requests

URL = Text
AtomicTypes = Union[int, float, Text, bool]
AD_ID_PATTERN = r'([0-9]{15})'


def get_ad_id_from_url(url: URL) -> Text:
    return re.search(AD_ID_PATTERN, url)[0]


def get_ads_from_search_results(ad_urls: List[URL],
                                previous_ads: pd.DataFrame) -> pd.DataFrame:
    results = pd.DataFrame()
    for i, url in enumerate(ad_urls):
        ad_id = get_ad_id_from_url(url)
        if ad_id in previous_ads.index:
            continue
        ad = Advert(url)
        df = pd.DataFrame(data=[ad.contents], index=[ad_id])
        results = pd.concat([results, df])
    print(f"Scraped {len(results)} new ads")
    return results


class Advert:
    def __init__(self, url: URL):
        self.url = url
        self.id = get_ad_id_from_url(url)
        self._contents = None

    def __repr__(self):
        return json.dumps(self.contents)

    @property
    def contents(self):
        if not self._contents:
            self._contents = self.scrape()
        return self._contents

    def scrape(self) -> Dict[Text, AtomicTypes]:
        url_id = re.findall('[0-9]{11,}', self.url)[0]
        base_url = 'https://www.autotrader.co.uk/json/fpa/initial/'
        request_url = f"{base_url}{url_id}"
        response = requests.get(request_url, timeout=5)

        if response.status_code != 200:
            raise ValueError(f"Unable to retrieve ad from: {request_url}")

        nested_properties = json.loads(response.content.decode('utf-8'))
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

        return flattened_properties


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
