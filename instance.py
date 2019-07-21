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
        self.csv_headers = False
        self.output_names = [
            'instance',
            'active',
            'ip_address',
            'version',
            'hostname',
            'as',
            'isp',
            'city',
            'regionName',
            'country',
            'countryCode',
            'lat',
            'lon'
            ]
        self.instance = {}

        for i in self.output_names:
            # print(i)
            self.instance[i] = None
        
        self.instance['instance'] = instance

    def debug_print(self, message):
        """Prints debugging messages"""
        if self.debug:
            print(message)

    def format_output_headers(self):
        csv_output = ''
        for name in self.output_names:
            csv_output += "%s," % name
        # Remove trailing comma
        return csv_output[:-1]

    def format_output(self, output='json'):
        """Formats output"""
        #TODO: Add Google sheets output
        if output == 'json':
            return self.instance
            # TODO: Run through and convert to json
        if output in ['sheets', 'csv']:
            csv_output = ''
            for name in self.output_names:
                csv_output += "%s," % self.instance[name]

            # Remove trailing comma
            return csv_output[:-1]
        else:
            print('Invalid output format')


    def check_hostname_valid(self, path=None):
        """Checks hostname has DNS entry and responds to HTTP GET"""
        try:
            # Check if the DNS name resolves
            self.instance['ip_address'] = socket.gethostbyname('cn%s.awmdm.com' % self.instance['instance'])

            # Test HTTP Request
            try:
                # GET index
                rest = REST('cn%s.awmdm.com/%s' % (self.instance['instance'], path), timeout=2, retries=2)
                if rest.get('').status_code == 200:
                    self.debug_print('\t Active')
                    self.instance['active'] = True
                else:
                    # Non 200 response, mark as inactive
                    self.instance['active'] = False

            # Catch Timeout or Connection Errors and mark as inactive
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
                self.debug_print('\t - HTTP timeout')
                self.instance['active'] = False

        # Catch DNS SERVFAIL
        except socket.gaierror:
            self.debug_print('\t - DNS error')
            self.instance['active'] = False

        return self.instance['active']

    def get_version(self):
        """Get instance version"""
        # Create REST instance
        rest = REST(url='cn%s.awmdm.com' % self.instance['instance'], debug=self.debug)

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

            self.instance['version'] = version
            self.debug_print('\t Version: %s' % self.instance['version'])
        elif response.status_code == 403:
            self.instance['version'] = 'API Protected'

        # API could be behind an auth wall
        # Leave as None
        return self.instance['version']

    def check_redirection(self):
        """Checks if an instance redirects to a company hostname"""
        # Get base URL
        rest = REST(url='cn%s.awmdm.com' % self.instance['instance'], debug=self.debug)
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

            self.instance['hostname'] = hostname
            self.debug_print('\t Hostname: %s' % self.instance['hostname'])

        return self.instance['hostname']

    def get_location(self):
        """Lookup IP location"""
        # For some reason this IP API fails without a user agent
        headers = {'User-Agent': 'Mozilla/5.0'}

        # Create REST instance to Geo check IP
        rest = REST(url='ip-api.com', protocol='http', debug=self.debug, headers=headers)

        # Query API
        response = rest.get('/json/%s' % self.instance['ip_address'])

        # If succesful parse json and set location
        if response.status_code == 200:
            response = json.loads(response.text)

            # Remove comma from AS and ORG field
            for field in ['as', 'org']:
                response[field] = response[field].replace(',', '')
            
            location = {}
            for name in [
                'as',
                'isp',
                'city',
                'regionName',
                'country',
                'countryCode',
                'lat',
                'lon']:
                self.instance[name] = response[name]
                location[name] = response[name]

        return location
