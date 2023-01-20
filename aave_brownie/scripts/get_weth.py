from scripts.helpers import get_account
from brownie import interface, config, network, accounts


def main():
    get_weth()


def get_weth():
    """
        Mints Weth by depositing eth

    """
    # abi
    # address
    account = get_account()

    weth = interface.IWeth(
        config["networks"][network.show_active()]['weth_token'])
    tx = weth.deposit({"from": account, "value": 0.1*10**18})
    tx.wait(1)
    print(f"recieved 0.1 weth")
    return tx
