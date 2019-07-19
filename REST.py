import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# Used for all AW REST API queries
class REST():
    """REST API Framework"""

    # Add the varibles as self.
    def __init__(self, url='', timeout=10, retries=5, headers=None, proxy=None, debug=False):
        # Import Proxy Server settings
        self.proxies = proxy
        self.url = url
        self.debug = debug
        self.timeout = timeout
        self.retries = retries

        # Start the session
        self.sessions = requests.Session()
        if isinstance(headers, dict):
            self.sessions.headers.update(headers)

        retries = Retry(total=self.retries, backoff_factor=1, status_forcelist=[502, 503, 504])
        self.sessions.mount('https://', HTTPAdapter(max_retries=retries))

        # Debugging
        if self.debug:
            print('API URL: %s' % self.url)
            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.setLevel(logging.DEBUG)
            requests_log.propagate = True

    # HTTP GET, returns HTTP response object
    def get(self, path):
        "HTTP GET"
        connection = self.sessions.get(
            'https://'+self.url+path, proxies=self.proxies, timeout=self.timeout)
        return connection

    # HTTP POST, returns HTTP response object
    def post(self, path, payload=None):
        """HTTP POST"""
        connection = self.sessions.post(
            'https://'+self.url+path, json=payload, proxies=self.proxies, timeout=self.timeout)
        return connection

    # HTTP PUT, returns HTTP response object
    def put(self, path, payload):
        """HTTP PUT"""
        connection = self.sessions.put(
            'https://'+self.url+path, data=payload, proxies=self.proxies, timeout=self.timeout)
        return connection

    # HTTP DELETE, returns HTTP response object
    def delete(self, path):
        """HTTP DELETE"""
        connection = self.sessions.delete(
            'https://'+self.url+path, proxies=self.proxies, timeout=self.timeout)
        return connection

    def response_headers(self, path):
        """Gets response headers"""
        connection = self.sessions.get(
            'https://'+self.url+path, proxies=self.proxies, timeout=self.timeout)
        return connection.headers
