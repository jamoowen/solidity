from brownie import FundMe
from scripts.helpers import get_account


def fund():
    fund_me = FundMe[-1]
    account = get_account()
    entrance = fund_me.getEntranceFee()
    print("entry fee:", entrance)
    print("fundin...")
    fund_me.fund({"from": account, "value": entrance})


def withdraw():
    fund_me = FundMe[-1]
    account = get_account()
    fund_me.withdraw({"from": account})


def main():
    fund()
    withdraw()
