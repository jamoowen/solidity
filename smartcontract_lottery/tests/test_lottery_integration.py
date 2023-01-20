from brownie import network
import pytest
from scripts.helpers import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, get_contract, fund_with_link
from scripts.deploy_lottery import deploy_lottery
import time


def test_can_pick_winner():
    start_time = time.time()
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    lottery = deploy_lottery()
    print(f"lottery deployed, {time.time()-start_time} seconds")
    account = get_account()
    lottery.startLottery(
        {"from": account, "gas_price": 45000000000, "gas_limit": 2000000})
    lottery.enter({"from": account, "gas_price": 45000000000,
                  "gas_limit": 2000000, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "gas_price": 45000000000,
                  "gas_limit": 2000000, "value": lottery.getEntranceFee()})
    print(f"lottery entered, {time.time()-start_time} seconds")
    fund_with_link(lottery.address)
    print(f"lottery funded, {time.time()-start_time} seconds")
    lottery.endLottery(
        {"from": account, "gas_price": 50000000000, "gas_limit": 5000000})
    time.sleep(300)
    print(f"lottery over  , {time.time()-start_time} seconds")
    print(f"random value= {lottery.randomWords()}")
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
