from scripts.deploy_lottery import deploy_lottery
from scripts.helpers import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, fund_with_link, get_contract
from brownie import Lottery, accounts, network, config, exceptions
from web3 import Web3
import pytest
import time


def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # arrange
    lottery = deploy_lottery()
    # act
    expected_entrance = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEntranceFee()
    # assert
    assert expected_entrance == entrance_fee


def test_cant_enter_unless_started():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # arrange
    lottery = deploy_lottery()
    # act
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter(
            {"from": get_account(), "value": lottery.getEntranceFee()})


def test_can_enter():
    # arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    # act
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    # assert
    assert lottery.players(0) == account


def test_can_end():
    # arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    # act
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery.address)
    lottery.endLottery({"from": account})
    # assert
    assert lottery.lottery_state() == 2


def test_pick_winner():
    # arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()

    # act
    lottery.startLottery({"from": account})

    starting_balance = account.balance()
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    print(f"account {account} just entered")
    account_2 = get_account(index=1)
    lottery.enter({"from": account_2,
                  "value": lottery.getEntranceFee()})
    print(f"account {account_2} just entered")
    account_3 = get_account(index=2)
    lottery.enter({"from": account_3,
                  "value": lottery.getEntranceFee()})
    print(f"account {account_3} just entered")
    tx = fund_with_link(lottery.address)
    tx.wait(1)

    starting_balance_of_lottery = lottery.balance()
    print(
        f"starting, recent winner = {lottery.recentWinner()}, acc balance = {starting_balance_of_lottery}")

    transaction = lottery.endLottery({"from": account})
    transaction.wait(1)
    id = transaction.events["RequestSent"]["requestId"]
    num_words = transaction.events["RequestSent"]["numWords"]
    STATIC_RNG = [777]
    coord_contract = get_contract("coordinator_address")
    wrapper_contract = get_contract("wrapperAddress")
    print("wrapper_sub_id =", wrapper_contract.SUBSCRIPTION_ID())
    coord_contract.fundSubscription(
        wrapper_contract.SUBSCRIPTION_ID(), 10*10**18)
    coord_contract.fulfillRandomWordsWithOverride(
        id, lottery.address, STATIC_RNG, {"from": account})
    print(
        f"ending recent winner = {lottery.recentWinner()}, acc balance end = {lottery.balance()}")

    # assert
    assert(lottery.recentWinner() == account)
    assert(lottery.balance() == 0)
    assert account.balance() == starting_balance+starting_balance_of_lottery

# ahweoiafheoi;hoaihwvaw
