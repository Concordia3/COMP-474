from tools_libs import requests

def search_wikidata(entity):
    url = 'https://www.wikidata.org/w/api.php'
    params = {
        'action': 'wbsearchentities',
        'format': 'json',
        'language': 'en',
        'search': entity
    }
    response = requests.get(url, params=params)
    return response.json()