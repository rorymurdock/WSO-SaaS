"""Module to check WSO SaaS instances"""
import socket
import json
import re
import requests
from REST import REST

class CheckInstance():
    """Class for all WSO SaaS Checking functions"""
    def __init__(self, instance, debug=False):
        self.debug = debug
        self.instance = instance
        self.active = None
        self.ip_address = None
        self.version = None
        self.hostname = None
        self.location = None

    def debug_print(self, message):
        """Prints debugging messages"""
        if self.debug:
            print(message)

    def format_output(self, output='json'):
        """Formats output"""
        #TODO: Add Google sheets output
        if output == 'json':
            output = {}
            output['instance'] = self.instance
            output['active'] = self.active
            output['IP'] = self.ip_address
            output['version'] = self.version
            output['hostname'] = self.hostname
            output['location'] = self.location
        elif output == 'csv':
            output = ('%s,%s,%s,%s,%s,%s' % (
                self.instance,
                self.active,
                self.ip_address,
                self.version,
                self.hostname,
                self.location)
                     )
        else:
            print('Invalid output format')
            output = None

        return output

    def check_hostname_valid(self, path=None):
        """Checks hostname has DNS entry and responds to HTTP GET"""
        try:
            # Check if the DNS name resolves
            self.ip_address = socket.gethostbyname('cn%s.awmdm.com' % self.instance)

            # Test HTTP Request
            try:
                # GET index
                rest = REST('cn%s.awmdm.com/%s' % (self.instance, path), timeout=2, retries=2)
                if rest.get('').status_code == 200:
                    self.debug_print('\t Active')
                    self.active = True
                else:
                    # Non 200 response, mark as inactive
                    self.active = False

            # Catch Timeout or Connection Errors and mark as inactive
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
                self.debug_print('\t - HTTP timeout')
                self.active = False

        # Catch DNS SERVFAIL
        except socket.gaierror:
            self.debug_print('\t - DNS error')
            self.active = False

        return self.active

    def get_version(self):
        """Get instance version"""
        # Create REST instance
        rest = REST(url='cn%s.awmdm.com' % self.instance, debug=self.debug)

        # At some stage the version file changed, try both
        urls = ['/api/help/local.json', '/api/system/help/localjson']

        # Try the first URL
        response = rest.get(urls[0])

        # If that 404's try the second URL
        if response.status_code == 404:
            response = rest.get(urls[1])

        # If this 200 OKs
        if response.status_code == 200:
            # Get the text, parse is
            versions = json.loads(response.text)
            version = versions['apis'][0]['products'][0]

            # Regex it to remove AirWatch and VMWare Workspace ONE UEM strings
            # Leaving just the version number
            version = re.match(
                r'(AirWatch|VMware Workspace ONE UEM);(.*)',
                version,
                re.M|re.I
                ).group(2)

            self.version = version
            self.debug_print('\t Version: %s' % self.version)

        # API could be behind an auth wall
        # Leave as None
        return self.version

    def check_redirection(self):
        """Checks if an instance redirects to a company hostname"""
        # Get base URL
        rest = REST(url='cn%s.awmdm.com' % self.instance, debug=self.debug)
        response = rest.get('')

        # If response array isn't empty then we have been redirected
        if response.history:
            # Get the final URL and extract the hostname in regex
            try:
                # Use regex to extract URL, for SAML catch identity service / login
                #TODO: Fix nike login match
                hostname = re.match(
                    r'https:\/\/(.*)\/(AirWatch|IdentityService)',
                    response.url,
                    re.M|re.I
                    ).group(1)

            # Unable to regex match, just use the whole URL
            except AttributeError:
                hostname = response.url

            self.hostname = hostname
            self.debug_print('\t Hostname: %s' % self.hostname)

        return self.hostname

    def get_location(self):
        """Lookup IP location"""
        # For some reason this IP API fails without a user agent
        headers = {'User-Agent': 'Mozilla/5.0'}

        # Create REST instance to Geo check IP
        rest = REST(url='ip-api.com', protocol='http', debug=self.debug, headers=headers)

        # Query API
        response = rest.get('/json/%s' % self.ip_address)

        # If succesful parse json and set location
        if response.status_code == 200:
            response = json.loads(response.text)
            self.location = "\"%s, %s, %s\", %s, %s" % (
                response['city'],
                response['regionName'],
                response['country'],
                response['as'],
                response['org']
                )

        return self.location
