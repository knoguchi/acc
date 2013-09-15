import logging
from money import Money
from acc.exception import ImmutableTransactionException, UnableToPostException
from acc.entry import Entry

log = logging.getLogger(__name__)


class Transaction(object):
    """
    Multi-Legged.
    must be new style class that inherits object so that
    type(self) returns proper class name
    """

    def __init__(self, date):
        self.date = date
        self.entries = []
        self.was_posted = False

    def add(self, amount, account):
        if self.was_posted:
            raise ImmutableTransactionException(
                "Cannot add entry to a transaction that's already posted")
        self.entries.append(Entry(amount, self.date,
                                  account=account,
                                  transaction=self))

    def post(self):
        if not self.can_post():
            raise UnableToPostException()
        for entry in self.entries:
            entry.post()
        self.was_posted = True

    def can_post(self):
        return self.balance() == 0

    def balance(self):
        if len(self.entries) == 0:
            # XXX: this should be currency neutral 0. or should this class
            # keep Currency?
            return Money(0, 'USD')
        result = None
        for entry in self.entries:
            if result is None:
                result = entry.get_amount()
                continue
            result += entry.get_amount()
        return result