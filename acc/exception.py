__author__ = 'kenji'

class AccountingException(Exception):
    pass


class RuntimeException(AccountingException):
    pass


class ImmutableEntryException(AccountingException):
    pass


class UnableToPostException(AccountingException):
    pass


class ImmutableTransactionException(AccountingException):
    pass
