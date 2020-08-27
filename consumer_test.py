import json
import logging
import os

import pytest
import requests
from requests.auth import HTTPBasicAuth

from pact import Consumer, Provider, Like, EachLike, Format

from conzoomer import getActiveAccounts, getAccount, PROVIDER_PORT, PROVIDER_HOST

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
print(Format().__dict__)

# Broker setup
PACT_UPLOAD_URL = (
    "http://127.0.0.1/pacts/provider/AccountJSService/consumer"
    "/PythonConzoomer/version"
)
PACT_FILE = "PythonConzoomer-AccountJSService.json"
PACT_BROKER_USERNAME = "pactbroker"
PACT_BROKER_PASSWORD = "pactbroker"
# PACT_MOCK_HOST = 'localhost'
# PACT_MOCK_PORT = 1234
PACT_DIR = os.path.dirname(os.path.realpath(__file__))
CONSUMER_VERSION = 4.2

# pact.start_service()
# atexit.register(pact.stop_service)


# class GetUserInfoContract(unittest.TestCase):

@pytest.fixture(scope='session')
def pact(request):
    pact = Consumer('PythonConzoomer').has_pact_with(Provider('AccountJSService'),
                                                    host_name=PROVIDER_HOST,
                                                    port=PROVIDER_PORT,
                                                    pact_dir=PACT_DIR)
    # V: Provider port must align with inner Consumer call setup! (Might be python thing)
    # V: Therefore I'm pulling definition for local development from Consumer directly
    try:
        print('start service')
        pact.start_service()
        yield pact
    finally:
        print('stop service')
        pact.stop_service()

    # version = request.config.getoption('--publish-pact')
    version = CONSUMER_VERSION
    # version = False
    if not request.node.testsfailed and version:
        push_to_broker(version)


def test_get_account(pact):
    expected = {
        'name': Like('A'),
        'account_number': 'XQR9MUP',
        'amount': Like(4000)
    }
    # Usage of Like:
    # Like(123)  # Matches if the value is an integer
    # Like('hello world')  # Matches if the value is a string
    # Like(3.14)  # Matches if the value is a float

    (pact
     .given('Account A exists and has balance and activity fields')
     .upon_receiving('a request for Account A')
     .with_request('get', '/accounts/num/XQR9MUP')
     .will_respond_with(200, body=expected))

    (pact
     .given('Active accounts exists')
     .upon_receiving('Request for Active accounts, return list')
     .with_request('get', '/accounts/active')
     .will_respond_with(200, body=EachLike(expected)))

    # pact.setup()

    with pact:
        acc = getAccount('XQR9MUP')
        activeAccs = getActiveAccounts()
        # print(acc)
        assert acc['name'] == 'A'
        assert activeAccs[0]['name'] == 'A'

    # pact.verify()
    # self.assertEqual(result, expected)


def push_to_broker(version):
    """
    Push to broker
    """
    with open(os.path.join(PACT_DIR, PACT_FILE), 'rb') as pact_file:
        pact_file_json = json.load(pact_file)

    basic_auth = HTTPBasicAuth(PACT_BROKER_USERNAME, PACT_BROKER_PASSWORD)

    log.info("Uploading pact file to pact broker...")

    r = requests.put(
        "{}/{}".format(PACT_UPLOAD_URL, version),
        auth=basic_auth,
        json=pact_file_json
    )
    if not r.ok:
        log.error("Error uploading: %s", r.content)
        r.raise_for_status()
