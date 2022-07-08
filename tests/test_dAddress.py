import pytest


def test_mint_address_book(dAddress, bob):
    bookName = "Book 1"

    assert dAddress.balanceOf(bob) == 0
    assert dAddress.totalSupply() == 0

    tx = dAddress.mint(bob, bookName, {"from": bob})
    tokenId = tx.return_value

    assert tokenId == dAddress.totalSupply()
    assert tokenId == 1

    assert dAddress.balanceOf(bob) == 1
    assert dAddress.ownerOf(1) == bob
    assert dAddress.tokenOfOwnerByIndex(bob, 0) == 1

    assert dAddress.bookName(1) == bookName
    assert dAddress.bookId(bookName) == 1
