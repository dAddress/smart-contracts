import os
import json

from brownie import DAddress, accounts
from brownie.network import max_fee, priority_fee, show_active, chain

bookName = "dAddress Book"


def main():
    priority_fee("2 gwei")
    max_fee("25 gwei")

    if show_active() == "development":
        deployer = accounts[0]
    else:
        account_name = "DEPLOYER_ACCOUNT_" + show_active().upper()
        print(account_name)

        deployer = accounts.load(os.environ.get(account_name))
        print(deployer)

    dAddress = DAddress.deploy(
        "dAddress Book",
        "dAB",
        "https://" + show_active() + ".daddress.org/api/token/{id}",
        0,
        {"from": deployer},
    )

    with open("./manifests/" + str(chain.id) + ".json", "w") as outfile:
        manifest = {"dAddress": dAddress.address, "network": show_active()}
        json.dump(manifest, outfile)

    dAddress.mint(deployer, bookName, {"from": deployer})
    dAddress.setAddress(bookName, "root", dAddress, {"from": deployer})
