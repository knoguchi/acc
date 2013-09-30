import datetime

from money.Money import Money, Currency, set_default_currency

from acc.constants import ACCOUNT_TYPE, EVENT_TYPE
from acc.account import Account
from acc.event import Event
from acc.entry import Entry
from acc.agreement import Agreement
from acc.posting_rule import PostingRule
from acc.utils import copy_accounts
set_default_currency('USD')


class ServiceAgreement(Agreement):
    def __init__(self):
        self.rate = None
        super(ServiceAgreement, self).__init__()

    def get_rate(self):
        return self.rate

    def set_rate(self, new_rate):
        self.rate = new_rate


class Customer:
    def __init__(self, name):
        self._name = name
        self._service_agreement = None

        self.accounts = None
        self.saved_real_accounts = None

        self.entries = []
        self.setup_accounts()

    def get_accounts(self):
        return self.accounts

    def set_accounts(self, accounts):
        self.accounts = accounts

    def setup_accounts(self):
        self.accounts = {}
        for account_type in ACCOUNT_TYPE.values():
            self.accounts[account_type] = Account(Currency('USD'), account_type)

    def account_for(self, account_type):
        assert isinstance(self.accounts[account_type], Account), "%s is not Account" % self.accounts[account_type]
        return self.accounts[account_type]

    def add_entry(self, arg, entry_type):
        assert type(arg) == Entry
        self.account_for(entry_type).post(arg)

    def get_entries(self):
        # make it unmodifiable
        return tuple(self.entries)

    def get_service_agreement(self):
        return self._service_agreement

    def set_service_agreement(self, arg):
        assert type(arg) == ServiceAgreement
        self._service_agreement = arg

    def balance_for(self, key):
        return self.account_for(key).balance()

    def process(self, event):
        rule = self.get_service_agreement().get_posting_rule(event.event_type,
                                                             event.occurred_at)
        assert rule is not None, "missing posting rule"
        rule.process(event)

    def begin_adjustment(self):
        """
        http://martinfowler.com/eaaDev/DifferenceAdjustment.html
        """
        assert not self.is_adjusting()
        # must be deep copy
        self.saved_real_accounts = self.accounts
        self.accounts = copy_accounts(self.saved_real_accounts)

    def is_adjusting(self):
        return self.saved_real_accounts is not None

    def commit_adjustment(self, adjustment):
        assert self.is_adjusting()
        for account_type in ACCOUNT_TYPE.values():
            self.adjust_account(account_type, adjustment)
        self.end_shadow_accounts()

    def adjust_account(self, account_type, adjustment):
        corrected_account = self.accounts.get(account_type)
        original_account = self.saved_real_accounts.get(account_type)
        difference = corrected_account.balance() - original_account.balance()
        result = Entry(difference, datetime.date.today())
        original_account.post(result)
        adjustment.add_resulting_entry(result)

    def end_shadow_accounts(self):
        assert self.is_adjusting()
        self.accounts = self.saved_real_accounts
        self.saved_real_accounts = None


class MonetaryEvent(Event):
    def __init__(self, amount, event_type,
                 occurred_at, subject):
        super(MonetaryEvent, self).__init__(event_type, occurred_at, subject)
        self.amount = amount

    def get_amount(self):
        return self.amount


class TaxEvent(MonetaryEvent):
    def __init__(self, base_event, taxable_amount):
        super(TaxEvent, self).__init__(taxable_amount,
                                       EVENT_TYPE.TAX,
                                       base_event.occurred_at,
                                       base_event.subject)
        self.base_event = base_event
        base_event.friend_add_secondary_event(self)
        assert base_event.event_type != self.event_type, \
            "Probable endless recursion"


class Unit:
    class KWH:
        @classmethod
        def amount(cls, amount):
            return Unit(amount)

    def __init__(self, amount):
        self.amount = amount

    def get_amount(self):
        return self.amount


class Usage(Event):
    def __init__(self, amount, occurred_at, customer=None, adjusted_event=None):
        super(Usage, self).__init__(EVENT_TYPE.USAGE, occurred_at, customer,
                                    adjusted_event)
        self.amount = amount

    def get_amount(self):
        return self.amount

    def get_rate(self):
        return self.subject.get_service_agreement().get_rate()


class AmountFormulaPR(PostingRule):
    def __init__(self, multiplier, fixed_fee, entry_type):
        super(AmountFormulaPR, self).__init__(entry_type)
        self.multiplier = multiplier
        self.fixed_fee = fixed_fee

    def calculate_amount(self, evt):
        event_amount = evt.get_amount()
        return event_amount * self.multiplier + self.fixed_fee

    def is_taxable(self):
        return not (self.entry_type == ACCOUNT_TYPE.TAX)

    def process(self, event):
        super(AmountFormulaPR, self).process(event)
        if self.is_taxable():
            TaxEvent(event, self.calculate_amount(event)).process()


class MultiplyByRatePR(PostingRule):
    def __init__(self, entry_type):
        super(MultiplyByRatePR, self).__init__(entry_type)

    def is_taxable(self):
        return not (self.entry_type == ACCOUNT_TYPE.TAX)

    @classmethod
    def calculate_amount(cls, usage_event):
        return Money(
            usage_event.get_amount().get_amount() * usage_event.get_rate(), 'USD')

    def process(self, event):
        super(MultiplyByRatePR, self).process(event)
        if self.is_taxable():
            TaxEvent(event, self.calculate_amount(event)).process()