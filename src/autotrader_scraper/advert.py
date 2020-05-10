import collections
import json
import re
from typing import Text, Dict, Union, Mapping

import requests

URL = Text
AtomicTypes = Union[int, float, Text, bool]


class Advert:
    def __init__(self, url: URL):
        self.url = url
        self.contents = self.scrape()

    def __repr__(self):
        return json.dumps(self.contents)

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
