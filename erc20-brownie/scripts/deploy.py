from brownie import JKRToken
from scripts.helpers import get_account
from web3 import Web3

initial_supply = Web3.toWei(1000, "ether")


def deploy_token():
    account = get_account()
    token = JKRToken.deploy(initial_supply, {"from": account})
    print(token.name())
    pass


def main():
    deploy_token()
