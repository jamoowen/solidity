from scripts.helpers import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS
from scripts.deploy import deploy_fund_me
from brownie import network, accounts, exceptions
import pytest


def test_fund_and_withdraw():
    print('testing....')
    account = get_account()
    fund_me = deploy_fund_me()
    entrance = fund_me.getEntranceFee() + 100
    tx = fund_me.fund({"from": account, "value": entrance})
    tx.wait(1)
    assert fund_me.addressToAmountFunded(account.address) == entrance
    tx2 = fund_me.withdraw({"from": account})
    tx2.wait(1)
    assert fund_me.addressToAmountFunded(account.address) == 0


def test_only_only_can_withdraw():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("only for local testing")
    fund_me = deploy_fund_me()
    bad_actor = accounts.add()
    with pytest.raises(exceptions.VirtualMachineError):
        fund_me.withdraw({"from": bad_actor})
