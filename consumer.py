
import requests
import logging


base_uri = "http://localhost:8082"
uri = base_uri + '/accounts/num/XQR9MUP'
response = requests.get(uri)
if response.status_code == 404:
    logging.error(response.json())
else:
    name = response.json()['name']
    amount = response.json()['amount']
    print('name', name)
    logging.warning('amount %s', amount)
