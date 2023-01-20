from scripts.helpers import get_account, FORKED_LOCAL_ENVIRONMENTS, LOCAL_BLOCKCHAIN_ENVIRONMENTS
from brownie import config, network, interface
from scripts.get_weth import get_weth
from web3 import Web3

amount = Web3.toWei(0.1, "ether")
# amount = 0.1


def main():
    account = get_account()

    erc20_address = config["networks"][network.show_active()]["weth_token"]

    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    lending_pool = get_lending_pool()
    approve_erc20(amount, lending_pool.address, erc20_address, account.address)
    print("depositing...")
    print(
        f"erc20: {erc20_address}\n amount: {amount}\n account:{account.address}\n lending pool: {lending_pool.address}")
    tx = lending_pool.deposit(erc20_address, amount,
                              account.address, 0, {"from": account})
    tx.wait(1)
    print("deposited!")
    borrowable_eth, total_debt = get_borrow_data(lending_pool, account)
    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"])
    dai_to_borrow = (1/dai_eth_price) * (borrowable_eth*0.90)
    print(f"we will borrow {dai_to_borrow} DAI")
    # now we borrow
    dai_address = config["networks"][network.show_active()]["dai_token"]

    borrow_tx = lending_pool.borrow(dai_address, Web3.toWei(
        dai_to_borrow, 'ether'), 1, 0, account.address, {"from": account})
    borrow_tx.wait(1)
    print("you just borrowed dai")
    get_borrow_data(lending_pool, account)
    # repay_all(amount, lending_pool, account)
    # get_borrow_data(lending_pool, account)


def repay_all(amount, lending_pool, account):
    approve_erc20(Web3.toWei(amount, 'ether'), lending_pool,
                  config["networks"][network.show_active()]['dai_token'], account)
    repay_tx = lending_pool.repay(config["networks"][network.show_active(
    )]['dai_token'], amount, 1, account.address, {"from": account})
    repay_tx.wait(1)
    print("you just deposited, borrowed and repayed!")


def get_asset_price(price_feed_address):
    # abi
    # address
    dai_eth_price_feed = interface.IAggregatorV3(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    converted_price = Web3.fromWei(latest_price, 'ether')
    print(f"DAI/ETH price is {converted_price}")
    return(float(converted_price))


def get_borrow_data(lending_pool, account):
    (totalCollateralETH, totalDebtETH, availableBorrowsETH, currentLiquidationThreshold,
     ltv, healthFactor) = lending_pool.getUserAccountData(account.address)
    totalCollateralETH = Web3.fromWei(totalCollateralETH, "ether")
    totalDebtETH = Web3.fromWei(totalDebtETH, "ether")
    availableBorrowsETH = Web3.fromWei(availableBorrowsETH, "ether")
    currentLiquidationThreshold = Web3.fromWei(
        currentLiquidationThreshold, "ether")
    ltv = Web3.fromWei(ltv, "ether")
    healthFactor = Web3.fromWei(healthFactor, "ether")
    print(f"{totalCollateralETH} of ETH deposited")
    print(f"{totalDebtETH} of ETH borrowed")
    print(f"{availableBorrowsETH} of ETH is available to borrow ")
    return (float(availableBorrowsETH), float(totalDebtETH))


def approve_erc20(amount, spender, erc20_address, account):
    print("approving erc20 token")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("token approved")
    return(tx)
    # abi
    # address


def get_lending_pool():
    #  we can physically copy the abi OR use an interface
    # abi
    # address

    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active(
        )]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    print(f"lending pool address is {lending_pool_address}")
    lending_pool = interface.ILendingPool(
        lending_pool_address
    )
    return lending_pool
