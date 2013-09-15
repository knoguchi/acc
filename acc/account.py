from acc.utils import DateRange
import datetime
from money import Money
from acc.transaction import Transaction

class Account(object):
    """
    TODO: Account should use Quantity abstract class, not Money
    """
    def __init__(self, currency, account_type):
        self.entries = []
        self.currency = currency
        self.type = account_type

    # page 42 provides this signature but we don't ever need this.
    # def addEntry(self, amount, date):
    #     assert self.currency == amount.currency()
    #     #XXX: what's the entryType for this?
    #     self.entries.append(Entry(amount, date))

    def add_entry(self, entry):
        self.entries.append(entry)

    def balance(self, date=None, period=None):
        if date is None and period is None:
            date = datetime.date.today()
        period = DateRange.upto(date)
        result = Money(0, self.currency)
        for entry in self.entries:
            if period.includes(entry.get_date()):
                result += entry.get_amount()
        return result

    def deposits(self, period):
        result = Money(0, self.currency)
        for entry in self.entries:
            if period.includes(entry.date()) and entry.amount().is_positive():
                result += entry.amount()
        return result

    def withdrawals(self, period):
        result = Money(0, self.currency)
        for entry in self.entries:
            if period.includes(entry.date()) and entry.amount().is_negative():
                result += entry.amount()
        return result

    def withdraw(self, amount, target, date):
        # two-legged AT
        #AccountingTransaction(amount, self, target, date)

        # multi-legged AT
        trans = Transaction(date)
        trans.add(-amount, self)
        trans.add(amount, target)
        trans.post()

    def post(self, arg):
        self.entries.append(arg)
