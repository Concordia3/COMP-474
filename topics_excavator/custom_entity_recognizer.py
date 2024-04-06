from tools_libs import requests

# function to query Wikidata for information about a compound word
def custom_entity_recognizer(compound_word):

    # convert the compound word to a string if it is not already
    if not isinstance(compound_word, str):
        compound_word = str(compound_word)

    # define the Wikidata API endpoint
    api_endpoint = "https://www.wikidata.org/w/api.php"

    # construct the parameters for the API request
    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": "en",
        "search": compound_word.lower(),
    }

    # send the API request
    response = requests.get(api_endpoint, params=params)

    # parse the JSON response
    data = response.json()

    # add data
    description = ''
    url = ''
    if data.get("search"):
        description = data["search"][0].get('description', ' ')
        url         = data["search"][0].get('url', ' ')

    return (compound_word.lower(), url, description)