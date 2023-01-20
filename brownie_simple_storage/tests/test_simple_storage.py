from brownie import SimpleStorage, accounts

#  just run brownie test
# will look for a name under tests/test_xxxx


def test_deploy():
    # 1. arrange
    account = accounts[0]

    # 2. act
    simple_storage = SimpleStorage.deploy({"from": account})
    starting_val = simple_storage.retrieve()
    expected = 0

    # 3. assert
    assert starting_val == expected


def test_updating_storage():
    # arrange
    account = accounts[0]
    simple_storage = SimpleStorage.deploy({"from": account})

    # act
    expected = 15
    simple_storage.store(expected, {"from": account})

    # assert
    assert expected == simple_storage.retrieve()
