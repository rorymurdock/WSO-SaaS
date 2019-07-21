"""Iterate through a range of numbers and check the WSO SaaS Instance"""
from instance import CheckInstance

INSTANCE_LIST = range(5000)
CHECKED_INSTANCE = []
OUTPUT = 'csv'

if OUTPUT == "csv":
    print(CheckInstance(0).format_output_headers())

for instance in INSTANCE_LIST:
    SAAS = CheckInstance(instance)
    if not SAAS.check_hostname_valid():
        CHECKED_INSTANCE.append(SAAS.format_output(output=OUTPUT))
    else:
        SAAS.get_version()
        SAAS.check_redirection()
        SAAS.get_location()
        CHECKED_INSTANCE.append(SAAS.format_output(output=OUTPUT))

    if OUTPUT == "csv":
        print(SAAS.format_output(output=OUTPUT))

if OUTPUT == "json":
    print(CHECKED_INSTANCE)
