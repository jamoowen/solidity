#  if you dont give brownie a url, it will load up using the ganache cli
# Brownie compiles, creates bytecode, creates abi automatically when
# you call brownie run scripts/deploy.py

# but you need address and private key

from brownie import accounts, config,  SimpleStorage, network
#


def deploy_simple_storage():
    # brownie has accounts built in from the ganache cli you open

    # you can set an account prvt key via cmd line: brownie accounts new <acc_name> <key>
    # account = accounts.load("test_account")
    account = get_account()
    simple_storage = SimpleStorage.deploy(
        {"from": account})
    stored_value = simple_storage.retrieve()
    transaction = simple_storage.store(
        15, {"from": account, "gas_price": 10000000000000000})
    transaction.wait(1)
    new_stored_value = simple_storage.retrieve()
    print(new_stored_value)


def get_account():
    if network.show_active() == "development":
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])


def main():
    deploy_simple_storage()
