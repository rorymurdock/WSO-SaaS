"""Test instance checker"""
from instance import CheckInstance

DNS_INACTIVE_INSTANCE = 0
HTTP_INACTIVE_INSTANCE = 40
ACTIVE_INSTANCE = 138
PROTECTED_API = 755
PROTECTED_API_HOSTNAME = 'swtadmin.awmdm.com'
STATIC_INSTANCE = 114
STATIC_INSTANCE_VERSION = '9.6'
UNIQUE_URL = 814
UNIQUE_URL_HOSTNAME = "nike.okta.com/login"

BASE_JSON = {}
BASE_JSON['instance'] = None
BASE_JSON['active'] = None
BASE_JSON['IP'] = None
BASE_JSON['version'] = None
BASE_JSON['hostname'] = None
BASE_JSON['location'] = None

def test_inactivate_instance():
    """Test inactive instance is marked as False"""
    # Test instance that has no DNS record
    saas = CheckInstance(DNS_INACTIVE_INSTANCE)

    # Set json to compare
    inactive_json = BASE_JSON
    inactive_json['active'] = False
    inactive_json['instance'] = 0

    assert saas.check_hostname_valid() is False
    assert saas.format_output() == inactive_json



    # Test instance that has a DNS record but doesn't response to HTTP
    saas = CheckInstance(HTTP_INACTIVE_INSTANCE)

    # Set json to compare
    inactive_json = BASE_JSON
    inactive_json['active'] = False
    inactive_json['instance'] = 40
    inactive_json['IP'] = '205.139.50.61'

    assert saas.check_hostname_valid() is False
    assert saas.format_output(output='csv') == "40,False,205.139.50.61,None,None,None"
    assert saas.format_output() == inactive_json


def test_activate_instance():
    """Test active instance is marked as True"""
    # Test a fully active
    saas = CheckInstance(ACTIVE_INSTANCE, debug=True)
    assert saas.check_hostname_valid() is True
    assert saas.check_hostname_valid(path='api/badpath') is False

def test_invalid_output():
    """Test invalid output method returns None"""
    saas = CheckInstance('')

    # Specify bad output
    assert saas.format_output(output='null') is None

def test_protected_api():
    """Test APIs behind a auth wall return None"""
    saas = CheckInstance(PROTECTED_API)
    assert saas.get_version() is None

def test_get_version():
    """Test instance version is accurate"""
    saas = CheckInstance(STATIC_INSTANCE)
    assert saas.get_version() == STATIC_INSTANCE_VERSION

def test_get_hostname():
    """Test hostnames are collected and parsed"""
    saas = CheckInstance(STATIC_INSTANCE)
    assert saas.check_redirection() == 'cn%s.awmdm.com' % STATIC_INSTANCE

    saas = CheckInstance(PROTECTED_API)
    assert saas.check_redirection() == PROTECTED_API_HOSTNAME

    saas = CheckInstance(UNIQUE_URL)
    assert UNIQUE_URL_HOSTNAME in saas.check_redirection()

def test_get_ip_location():
    """Test resolving an IP to a location"""
    saas = CheckInstance(ACTIVE_INSTANCE)
    assert saas.get_location() == 'Atlanta, Georgia, United States'
