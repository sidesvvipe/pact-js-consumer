import requests
import logging

PROVIDER_PORT = "8088"
PROVIDER_HOST = "localhost"


def getAccount(acc_num):
    uri = "http://" + PROVIDER_HOST + ":" + PROVIDER_PORT + "/accounts/num/" + acc_num
    print(requests.get(uri).json())
    return requests.get(uri).json()


def getActiveAccounts():
    uri = "http://" + PROVIDER_HOST + ":" + PROVIDER_PORT + "/accounts/active"
    print(requests.get(uri).json())
    return requests.get(uri).json()
