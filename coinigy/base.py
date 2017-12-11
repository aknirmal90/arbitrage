import os
import requests


class Coiningy(object):

    def __init__(self):
        self._base_url = 'https://api.coinigy.com/api/v1/'
        self._session = requests.Session()
        self._update_headers()

    def _update_headers(self):
        COININGY_USERNAME = os.getenv('COININGY_USERNAME')
        COININGY_APISECRET = os.getenv('COININGY_APISECRET')

        headers = (
            ('X-API-KEY', COININGY_USERNAME),
            ('X-API-SECRET', COININGY_APISECRET),
            ('Content-Type', 'application/json'),
        )
        self._session.headers.update(headers)

    def prepare_request(self, resource, params=None, method='GET'):
        _url = os.path.join(self._base_url, resource)
        return self._session.request(method=method, url=_url, json=params)
