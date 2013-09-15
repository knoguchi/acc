#from acc.account import Account, AccountingTransaction


class Entry(object):
    """
    Entry object.

    < Date | Account | EntryType | Amount >

    See page 23
    """

    def __init__(self, amount, entry_date,
                 account=None,
                 entry_type=None,
                 transaction=None):
        #print type(account), type(entryType), type(transaction)

        # amount and date must be set
        assert amount and entry_date

        # entryType for two-legged, account and transaction for multi-legged
        assert entry_type or (account and transaction)

        # type checking
        #assert account is None or type(account) == Account
        #assert entryType is None or type(entryType) == AccountType
        #assert transaction is None or type(transaction) == AccountingTransaction

        self.amount = amount
        self.entry_date = entry_date
        self.entry_type = entry_type

        # only used by AccountingTransaction
        self.account = account
        self.transaction = transaction

    def get_amount(self):
        return self.amount

    def get_date(self):
        return self.entry_date

    def get_entry_type(self):
        return self.entry_type

    def __str__(self):
        return "<Entry %s, %s, %s>" % (self.entry_type, self.entry_date, self.amount)

    def post(self):
        # only used by AccountingTransaction
        self.account.add_entry(self)
