import logging
import shutil

import requests

from ._core import DataSource, fetch_file

DEFAULT_CONNECT_TIMEOUT_SECS = 100

_log = logging.getLogger(__name__)


class CDSESource(DataSource):
    """
    Class for data retrievals using the Copernicus Data Space Ecosystem (CDSE) OData API.
    """

    def __init__(self, target_dir, api_url, download_url, oidc_url, username, password, query, show_progressbars=False,
                 timeout=DEFAULT_CONNECT_TIMEOUT_SECS, filename_transform=None, override_existing=False):
        self.target_dir = target_dir
        self.filename_transform = filename_transform
        self.override_existing = override_existing
        self.api_url = api_url
        self.download_url = download_url
        self.oidc_url = oidc_url
        self.username = username
        self.password = password
        self.query = query
        self.show_progressbars = show_progressbars
        self.timeout = timeout

    def _query_catalogue(self, query, products, next_url=None):
        url = next_url if next_url else self.api_url
        res = requests.get(url, params=query, timeout=self.timeout)

        if res.status_code != 200:
            _log.error('Failed to query CDSE catalogue: %s', res.text)
            return

        catalogue = res.json()
        products = products + catalogue['value']

        if '@odata.nextLink' in catalogue:
            return self._query_catalogue(query, products, catalogue['@odata.nextLink'])

        return products

    def _get_download_access_token(self):
        res = requests.post(self.oidc_url, data={
            'username': self.username,
            'password': self.password,
            'grant_type': 'password',
            'client_id': 'cdse-public'
        }, timeout=self.timeout)

        if res.status_code != 200:
            _log.error('Failed to get download access token: %s', res.text)
            return

        return res.json()['access_token']

    def trigger(self, reporter):
        """
        :type reporter: ResultHandler
        """

        def create_fetch_function(url, token):
            def cdse_fetch(target):
                headers = {
                    'Authorization': 'Bearer {token}'.format(token=token)
                }

                with requests.get(url, stream=True, headers=headers) as r, open(target, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)

                return True

            return cdse_fetch

        token = self._get_download_access_token()

        for product in self._query_catalogue(self.query, []):
            _log.info('Found %s with uuid %s', product['Name'], product['Id'])
            url = self.download_url.format(product_id=product['Id'])

            fetch_file(
                url,
                create_fetch_function(url, token),
                reporter,
                product['Name'],
                self.target_dir,
                filename_transform=self.filename_transform,
                override_existing=self.override_existing
            )
