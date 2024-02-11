import requests
from requests.adapters import HTTPAdapter, Retry


# def apografi_dictionary_get(endpoint):
#     url = f"{APOGRAFI_DICTIONARIES_URL}{endpoint}"
#     print(url)
#     headers = {"Accept": "application/json"}
#     response = requests.get(url, headers=headers)
#     return response.json()["data"]


def apografi_get(URL):
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount(URL, HTTPAdapter(max_retries=retries))
    headers = {"Accept": "application/json"}
    return session.get(URL, headers=headers)
