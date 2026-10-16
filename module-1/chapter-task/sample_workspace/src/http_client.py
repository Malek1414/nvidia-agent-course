import requests


def get(url, timeout=10):
    return requests.get(url, timeout=timeout)
