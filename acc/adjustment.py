from acc.event import Event
from acc.entry import Entry
from acc.constants import ACCOUNT_TYPE
import datetime


class DifferenceAdjustment(Event):
    def __init__(self, occurred_at, subject):
        super(DifferenceAdjustment, self).__init__(None, occurred_at, subject)
        self.new_events = []
        self.old_events = []

        self.savedAccounts = {}

    def add_new_event(self, arg):
        self.new_events.append(arg)

    def add_old_event(self, arg):
        if arg.has_been_adjusted():
            # IllegalArgumentException
            raise ValueError(
                "Cannot create " + str(
                    self) + ". " + arg + " is already adjusted")
        self.old_events.append(arg)
        arg.set_replacement_event(self)

    def reverse_old_events(self):
        for e in self.old_events:
            e.reverse()

    def process_replacements(self):
        for e in self.new_events:
            e.process()

    def process(self):
        assert not self.is_processed, "Cannot process an event twice"
        self.adjust()
        self.mark_processed()

    def adjust(self):
        self.snapshot_accounts()
        self.reverse_old_events()
        self.process_replacements()
        self.commit()

        self.secondary_events = self.old_events

    def copy_accounts(self, account_from):
        result = {}
        for t in account_from:
            result[t] = account_from.copy()
        return result

    def snapshot_accounts(self):
        saved_accounts = self.subject.get_accounts()
        self.subject.set_accounts(self.copy_accounts(saved_accounts))

    def reverse_old_events(self):
        for event in self.old_events:
            event.reverse()

    def process_replacements(self):
        for new_event in self.new_events:
            for i in range(len(new_event)):
                new_event[i].process()

    def commit(self):
        for t in ACCOUNT_TYPE.values():
            self.adjust_account(t)
        self.restore_accounts()

    def adjust_account(self, account_type):
        corrected_account = self.subject.account_for(account_type)
        original_account = self.get_saved_accounts().get(account_type)
        difference = corrected_account.balance().subtract(original_account.balance())
        result = Entry(difference, datetime.date.today())
        original_account.addEntry(result)
        self.resulting_entries.add(result)

    def restore_accounts(self):
        self.subject.set_accounts(self.saved_accounts)


class ReversalAdjustment(Event):
    def process(self):
        """
        override Event.process()
        """
        assert not self._is_processed, "Cannot process an event twice"
        if self.adjusted_event:
            self.adjusted_event.reverse()
        self._subject.process(self)
        self.mark_processed()


class ReplacementAdjustment(Event):

    def process(self):
        """
        override Event.process()
        """
        assert not self._is_processed, "Cannot process an event twice"
        if self.adjusted_event:
            self.adjusted_event.undo()
        self._subject.process(self)
        self.mark_processed()

