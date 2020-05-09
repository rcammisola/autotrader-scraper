import json
import re
from typing import Text, Dict, Any, List

import requests
from lxml import html


def ad_scraper(url: Text) -> Dict[Text, Any]:
    url_id = re.findall('[0-9]{11,}', url)[0]
    base_url = 'https://www.autotrader.co.uk/json/fpa/initial/'
    response = requests.get(f"{base_url}{url_id}", timeout=5)

    ret = dict()

    ret['url'] = url
    ret['status_code'] = response.status_code
    if response.status_code != 200:
        return ret

    ret['raw_response'] = response.content.decode('utf-8')

    d = json.loads(response.content.decode('utf-8'))

    keys_vehicle = {
        'make', 'model', 'trim', 'condition', 'tax', 'co2Emissions'
    }
    for nm in set(d['vehicle'].keys()).intersection(keys_vehicle):
        ret[nm] = d['vehicle'][nm]

    keys_spec = {
        'engine-size', 'manufactured-year', 'body-type', 'mileage',
        'transmission', 'fuel-type', 'doors', 'seats'
    }
    for nm in set(d['vehicle']['keyFacts'].keys()).intersection(keys_spec):
        ret[nm] = d['vehicle']['keyFacts'][nm]

    if 'doors' in ret.keys():
        match = re.search(r'\d+', ret['doors'])
        if match:
            ret['doors'] = match[0]

    if 'seats' in ret.keys():
        match = re.search(r'\d+', ret['seats'])
        if match:
            ret['seats'] = match[0]

    if 'manufactured-year' in ret.keys():
        match = re.search(r'\d{4}', ret['manufactured-year'])
        if match:
            ret['manufactured-year'] = match[0]

    if 'mileage' in ret.keys():
        ret['mileage'] = re.sub(r'[^\d\.]', '', ret['mileage'])

    if 'co2Emissions' in ret.keys():
        ret['co2Emissions'] = re.sub(r'[^\d\.]', '', ret['co2Emissions'])

    keys_advert = {'price', 'description'}
    for nm in set(d['advert'].keys()).intersection(keys_advert):
        ret[nm] = d['advert'][nm]

    if 'price' in ret.keys():
        ret['price'] = re.sub(r'[^\d]', '', ret['price'])

    keys_seller = {'isTradeSeller', 'townAndDistance', 'emailAddress'}
    for nm in set(d['seller'].keys()).intersection(keys_seller):
        ret[nm] = d['seller'][nm]

    for nm in set(d['pageData']['tracking'].keys()).intersection(keys_seller):
        ret[nm] = d['pageData']['tracking'][nm]

    for nm in list(ret.keys()):
        ret[re.sub('-', '_', nm)] = ret.pop(nm)

    return ret


def search_result_scraper(url: Text) -> List:
    response = requests.get(url, timeout=5)
    tree = html.fromstring(response.content.decode('utf-8'))
    res = set(tree.xpath('//a[contains(@class, "listing-fpa-link")]/@href'))
    return list(res)
