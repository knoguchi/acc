from unittest import TestCase
from datetime import date
from acc.event import EventList
from acc.transaction import Transaction
from acc.adjustment import DifferenceAdjustment, ReversalAdjustment

from tests.electricity import *


class ReallyEqualMixin(object):
    def assertReallyEqual(self, a, b):
        # assertEqual first, because it will have a good message if the
        # assertion fails.
        self.assertEqual(a, b)
        self.assertEqual(b, a)
        self.assertTrue(a == b)
        self.assertTrue(b == a)
        self.assertFalse(a != b)
        self.assertFalse(b != a)
        self.assertEqual(0, cmp(a, b))
        self.assertEqual(0, cmp(b, a))

    def assertReallyNotEqual(self, a, b):
        # assertNotEqual first, because it will have a good message if the
        # assertion fails.
        self.assertNotEqual(a, b)
        self.assertNotEqual(b, a)
        self.assertFalse(a == b)
        self.assertFalse(b == a)
        self.assertTrue(a != b)
        self.assertTrue(b != a)
        self.assertNotEqual(0, cmp(a, b))
        self.assertNotEqual(0, cmp(b, a))


class TestElectricityUsage(TestCase, ReallyEqualMixin):
    def setUp(self):
        self.acm = Customer("Acme Coffee Makers")
        standard = ServiceAgreement()
        standard.set_rate(10)
        standard.add_posting_rule(EVENT_TYPE.USAGE,
                                  MultiplyByRatePR(ACCOUNT_TYPE.BASE_USAGE),
                                  date(1999, 10, 1))
        standard.add_posting_rule(EVENT_TYPE.TAX,
                                  AmountFormulaPR(0.055, Money(0),
                                                  ACCOUNT_TYPE.TAX),
                                  date(1999, 10, 1))
        self.acm.set_service_agreement(standard)

    def getEntry(self, customer, t):
        entries = customer.get_entries()
        for e in entries:
            if e.get_entry_type() == t:
                return e

    def test_usage(self):
        """
        page 37
        """
        usage_evt = Usage(Unit.KWH.amount(50), date(1999, 10, 1), self.acm)
        usage_evt.process()

        # Entry getEntry(Customer, AccountType)
        usage_entry = self.acm.account_for(ACCOUNT_TYPE.BASE_USAGE).entries[0]
        tax_entry = self.acm.account_for(ACCOUNT_TYPE.TAX).entries[0]
        self.assertEqual(Money(500), usage_entry.get_amount())
        self.assertEqual(ACCOUNT_TYPE.BASE_USAGE, usage_entry.get_entry_type())
        self.assertEqual(Money(27.5), tax_entry.get_amount())
        self.assertEqual(ACCOUNT_TYPE.TAX, tax_entry.get_entry_type())

        self.assertIn(usage_entry, usage_evt.resulting_entries)
        self.assertIn(tax_entry, usage_evt.get_all_resulting_entries())

    def test_balanceUsingTransactions(self):
        """
        page 48
        """
        revenue = self.acm.account_for(ACCOUNT_TYPE.REVENUE)
        deferred = self.acm.account_for(ACCOUNT_TYPE.RECEIVABLES)
        receivables = self.acm.account_for(ACCOUNT_TYPE.DEFERRED)

        revenue.withdraw(Money(500), receivables, date(1999, 1, 4))
        revenue.withdraw(Money(200), deferred, date(1999, 1, 4))

        self.assertReallyEqual(Money(500), receivables.balance())
        self.assertReallyEqual(Money(200), deferred.balance())
        self.assertReallyEqual(Money(-700), revenue.balance())

    def test_balanceUsingMultiLeggedTransaction(self):
        revenue = self.acm.account_for(ACCOUNT_TYPE.REVENUE)
        deferred = self.acm.account_for(ACCOUNT_TYPE.RECEIVABLES)
        receivables = self.acm.account_for(ACCOUNT_TYPE.DEFERRED)

        multi = Transaction(date(2000, 1, 4))
        multi.add(Money(-700), revenue)
        multi.add(Money(500), receivables)
        multi.add(Money(200), deferred)
        multi.post()

        self.assertReallyEqual(Money(500), receivables.balance())
        self.assertReallyEqual(Money(200), deferred.balance())
        self.assertReallyEqual(Money(-700), revenue.balance())

    def test_ReversalAdjustment(self):
        """
        reversing incorrect accounting event
        """
        #setUpLowPay()

        # what initially posted
        usage_event = Usage(Unit.KWH.amount(50), date(1999, 10, 1), self.acm)
        # must read http://martinfowler.com/eaaDev/AgreementDispatcher.html
        event_list = EventList()
        event_list.add(usage_event)
        event_list.process()

        self.assertReallyEqual(Money(500), self.acm.balance_for(ACCOUNT_TYPE.BASE_USAGE))
        self.assertReallyEqual(Money(27.5), self.acm.balance_for(ACCOUNT_TYPE.TAX))

        # adjust
        correct_usage_event = Usage(Unit.KWH.amount(70), date(1999, 10, 1), self.acm)
        adjustment1 = ReversalAdjustment(correct_usage_event, date(1999, 11, 1),
                                         adjusted_event=usage_event)

        event_list.add(adjustment1)
        event_list.process()

        self.assertReallyEqual(Money(700), self.acm.balance_for(ACCOUNT_TYPE.BASE_USAGE))
        self.assertReallyEqual(Money(38.50), self.acm.balance_for(ACCOUNT_TYPE.TAX))

    def test_DifferenceAdjustment(self):

        usage1 = Usage(Unit.KWH.amount(20), date(1999, 10, 1), self.acm)
        usage2 = Usage(Unit.KWH.amount(20), date(1999, 10, 2), self.acm)
        usage3 = Usage(Unit.KWH.amount(30), date(1999, 10, 3), self.acm)

        event_list = EventList()
        event_list.add(usage1)
        event_list.add(usage2)
        event_list.add(usage3)
        event_list.process()

        # total 700kw, $700, $38.5 tax

        self.assertReallyEqual(Money(700), self.acm.balance_for(ACCOUNT_TYPE.BASE_USAGE))
        self.assertReallyEqual(Money(38.50), self.acm.balance_for(ACCOUNT_TYPE.TAX))

        # adjustment events

        new1 = Usage(Unit.KWH.amount(10), date(1999, 10, 1), self.acm)
        new2 = Usage(Unit.KWH.amount(10), date(1999, 10, 2), self.acm)
        new3 = Usage(Unit.KWH.amount(15), date(1999, 10, 3), self.acm)

        adj_date = date(2000, 1, 12)
        adj = DifferenceAdjustment(adj_date, self.acm)

        adj.add_old_event(usage1)
        adj.add_old_event(usage2)
        adj.add_old_event(usage3)

        adj.add_new_event(new1)
        adj.add_new_event(new2)
        adj.add_new_event(new3)

        event_list.add(adj)
        event_list.process()

        self.assertReallyEqual(Money(350), self.acm.balance_for(ACCOUNT_TYPE.BASE_USAGE))
        self.assertReallyEqual(Money(19.25), self.acm.balance_for(ACCOUNT_TYPE.TAX))
