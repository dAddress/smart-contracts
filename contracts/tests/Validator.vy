# @version 0.3.3

# 1. DECLARING INTERFACES

interface AddressValidator:
    def isValidContract(_bookName: String[16], _addressName: String[16]) -> bool: view

implements: AddressValidator

# 2. DECLARING EVENTS

# 3. DECLARING STORAGE VARIABLES
bookName: public(String[16])
addressName: public(String[16])

# 4. DECLARING CALLS AND FUNCTIONS

@external
def setAddressInfo(_bookName: String[16], _addressName: String[16]):
    self.bookName = _bookName
    self.addressName = _addressName

@view
@external
def isValidContract(_bookName: String[16], _addressName: String[16]) -> bool:
    return _bookName == self.bookName and _addressName == self.addressName