from brownie import ZERO_ADDRESS
import brownie
import pytest

bookName = "Book 1"


def test_mint_address_book(dAddress, bob):
    assert dAddress.balanceOf(bob) == 0
    assert dAddress.totalSupply() == 0

    tx = dAddress.mint(bob, bookName, {"from": bob})
    tokenId = tx.return_value

    assert tokenId == dAddress.totalSupply()
    assert tokenId == 1

    assert tx.events.count("Transfer") == 1
    log = tx.events["Transfer"][0]
    log["sender"] == ZERO_ADDRESS
    log["receiver"] == bob
    log["tokenId"] == 1

    assert tx.events.count("BookCreation") == 1
    log = tx.events["BookCreation"][0]
    assert log["owner"] == bob
    assert log["bookName"] == bookName

    assert dAddress.balanceOf(bob) == 1
    assert dAddress.ownerOf(1) == bob
    assert dAddress.tokenOfOwnerByIndex(bob, 0) == 1

    assert dAddress.bookName(1) == bookName
    assert dAddress.bookId(bookName) == 1


def test_mint_with_value(dAddress, owner, bob):
    dAddress.updateMinPrice("1 ether", {"from": owner})

    with brownie.reverts("Value sent is not enough"):
        dAddress.mint(bob, bookName, {"from": bob})

    dAddress.mint(bob, bookName, {"from": bob, "value": "2 ether"})
    assert dAddress.balance() > 0

    ownerBalance = owner.balance()
    dAddress.withdraw({"from": bob})
    assert owner.balance() > ownerBalance
    assert dAddress.balance() == 0


def test_mint_address_book_should_revert(dAddress, bob):
    with brownie.reverts("Book name cannot be empty"):
        dAddress.mint(bob, "", {"from": bob})

    dAddress.mint(bob, bookName, {"from": bob})

    with brownie.reverts("Book name already taken"):
        dAddress.mint(bob, bookName, {"from": bob})


def test_set_address(dAddress, bob):
    dAddress.mint(bob, bookName, {"from": bob})
    dAddress.setAddress(bookName, "Bob", bob, {"from": bob})

    assert dAddress.dAddressOf(bookName, "Bob") == bob


def test_set_address_should_revert(dAddress, bob, alice):
    dAddress.mint(bob, bookName, {"from": bob})

    with brownie.reverts("Invalid Address Book"):
        dAddress.setAddress("wrong book name", "Bob", bob, {"from": bob})

    with brownie.reverts():
        dAddress.setAddress(bookName, "Bob", bob, {"from": alice})


def test_set_valid_address(dAddress, validator, bob):
    addressName = "Contract Name"

    validator.setAddressInfo(bookName, addressName, {"from": bob})

    dAddress.mint(bob, bookName, {"from": bob})
    dAddress.setAddress(bookName, addressName, validator, True, {"from": bob})

    assert dAddress.dAddressOf(bookName, addressName) == validator
    assert dAddress.validateContract(bookName, addressName)

    validator.setAddressInfo(bookName, "something else", {"from": bob})
    with brownie.reverts("Not valid"):
        dAddress.validateContract(bookName, addressName)

    dAddress.setAddress(bookName, addressName, bob, True, {"from": bob})
    with brownie.reverts("Not a contract"):
        dAddress.validateContract(bookName, addressName)


def test_transfer(dAddress, bob, alice):
    dAddress.mint(bob, bookName, {"from": bob})
    assert dAddress.balanceOf(bob) == 1
    assert dAddress.ownerOf(1) == bob
    assert dAddress.tokenOfOwnerByIndex(bob, 0) == 1

    dAddress.mint(alice, "Book 2", {"from": bob})
    assert dAddress.balanceOf(alice) == 1
    assert dAddress.ownerOf(2) == alice
    assert dAddress.tokenOfOwnerByIndex(alice, 0) == 2

    dAddress.transferFrom(bob, alice, 1, {"from": bob})
    assert dAddress.balanceOf(bob) == 0
    with brownie.reverts():
        dAddress.tokenOfOwnerByIndex(bob, 0)
    assert dAddress.ownerOf(1) == alice
    assert dAddress.balanceOf(alice) == 2
    assert dAddress.tokenOfOwnerByIndex(alice, 0) == 2
    assert dAddress.tokenOfOwnerByIndex(alice, 1) == 1


def test_safe_transfer(dAddress, receiver, bob):
    dAddress.mint(bob, bookName, {"from": bob})
    assert dAddress.balanceOf(bob) == 1
    assert dAddress.ownerOf(1) == bob
    assert dAddress.tokenOfOwnerByIndex(bob, 0) == 1

    receiver.setTokenOwner(dAddress, 1, {"from": bob})
    dAddress.safeTransferFrom(bob, receiver, 1, {"from": bob})
    assert dAddress.balanceOf(bob) == 0
    with brownie.reverts():
        dAddress.tokenOfOwnerByIndex(bob, 0)
    assert dAddress.ownerOf(1) == receiver
    assert dAddress.balanceOf(receiver) == 1
    assert dAddress.tokenOfOwnerByIndex(receiver, 0) == 1

    receiver.returnToken(dAddress, 1, {"from": bob})
    assert dAddress.balanceOf(bob) == 1
    with brownie.reverts():
        dAddress.tokenOfOwnerByIndex(receiver, 0)
    assert dAddress.ownerOf(1) == bob
    assert dAddress.balanceOf(receiver) == 0
    assert dAddress.tokenOfOwnerByIndex(bob, 0) == 1


def test_transfer_approval(dAddress, owner, bob, alice):
    dAddress.mint(bob, bookName, {"from": bob})
    dAddress.mint(bob, "Book 2", {"from": bob})
    dAddress.mint(bob, "Book 3", {"from": bob})
    dAddress.approve(alice, 2, {"from": bob})

    with brownie.reverts():
        dAddress.transferFrom(bob, alice, 2, {"from": owner})

    dAddress.transferFrom(bob, owner, 2, {"from": alice})
    assert dAddress.balanceOf(bob) == 2
    assert dAddress.balanceOf(owner) == 1

    dAddress.approve(alice, 1, {"from": bob})
    assert dAddress.getApproved(1) == alice

    dAddress.approve(ZERO_ADDRESS, 1, {"from": bob})
    with brownie.reverts():
        dAddress.transferFrom(bob, owner, 1, {"from": alice})

    dAddress.setApprovalForAll(owner, True, {"from": bob})
    assert dAddress.isApprovedForAll(bob, owner)

    dAddress.transferFrom(bob, alice, 1, {"from": owner})
    assert dAddress.balanceOf(alice) == 1


def test_ownership_change(dAddress, owner, bob):
    assert dAddress.owner() == owner

    dAddress.updateOwner(bob, {"from": owner})
    assert dAddress.pendingOwner() == bob
    assert dAddress.owner() == owner

    dAddress.acceptOwnership({"from": bob})
    assert dAddress.owner() == bob
    assert dAddress.pendingOwner() == ZERO_ADDRESS
