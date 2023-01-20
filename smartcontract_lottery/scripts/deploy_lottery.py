from scripts.helpers import get_account, get_contract, fund_with_link
from brownie import Lottery, network, config
import time


def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("link_token").address,
        get_contract("wrapperAddress").address,
        {"from": account, "gas_price": 45000000000, "gas_limit": 5000000},
        publish_source=config["networks"][network.show_active()].get(
            "verify", False)
    )
    print("deployed lottery!")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    starting_tx = lottery.startLottery(
        {"from": account, "gas_price": 45000000000, "gas_limit": 2000000})
    starting_tx.wait(1)
    print("started the lottery\n")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 1000000
    tx = lottery.enter({"from": account, "gas_price": 45000000000,
                       "gas_limit": 2000000, "value": value})
    tx.wait(1)
    print("you entered the lottery")


def end_lottery():
    print("about to end the lottery... \n ...")

    account = get_account()
    lottery = Lottery[-1]
    # fund the contract then end the lottery
    # print("balance:", lottery.get_balance())
    tx = fund_with_link(lottery.address)
    tx.wait(1)
    print("here!", lottery.calcPrice())
    ending_tx = lottery.endLottery(
        {"from": account, "gas_price": 45000000000, "gas_limit": 5000000})
    ending_tx.wait(1)
    time.sleep(300)

    print(f"{lottery.recentWinner()} is the recent winner")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
