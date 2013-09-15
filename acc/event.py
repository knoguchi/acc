__author__ = 'kenji'
from acc.entry import Entry
import datetime
import logging

log = logging.getLogger()

class Event(object):
    def __init__(self, event_type, occurred_at,
                 subject=None, adjusted_event=None):
        assert subject or adjusted_event
        #assert subject is None or issubclass(subject.__class__, Subject)
        assert adjusted_event is None or issubclass(adjusted_event.__class__,
                                                   Event)

        self._event_type = event_type
        self._occurred_at = occurred_at
        self._notified_at = datetime.date.today()
        self._subject = subject
        self._resulting_entries = []  # hash map?
        self._secondary_events = []

        # for reversal adjustment
        self.adjusted_event = None
        self.replacement_event = None
        if adjusted_event:
            if self.adjusted_event and self.adjusted_event.has_been_adjusted():
                #IllegalArgumentException
                raise ValueError(
                    "The " + adjusted_event + "is already adjusted")
            self.adjusted_event = adjusted_event
            if not self._subject:
                self._subject = adjusted_event.subject
            self.adjusted_event.replacement_event = self

        self._is_processed = False

    def has_been_adjusted(self):
        """
        page 56
        """
        return self.replacement_event is not None

    @property
    def subject(self):
        return self._subject or self.adjusted_event.subject

    @property
    def event_type(self):
        return self._event_type

    @property
    def notified_at(self):
        return self._notified_at

    @property
    def occurred_at(self):
        return self._occurred_at

    def add_resulting_entry(self, arg):
        self._resulting_entries.append(arg)

    @property
    def resulting_entries(self):
        return self._resulting_entries

    @property
    def secondary_events(self):
        return self._secondary_events

    def find_rule(self):
        """
        page 26
        """
        rule = self.subject.get_service_agreement().get_posting_rule(
            self._event_type, self._occurred_at)
        assert rule is not None, "missing posting rule"
        return rule

    def mark_processed(self):
        self._is_processed = True

    @property
    def is_processed(self):
        return self._is_processed

    def process(self):
        """
        page 26, 57, 71
        """
        assert not self._is_processed, "Cannot process an event twice"
        if self.adjusted_event:
            self.adjusted_event.reverse()
        self._subject.process(self)
        self.mark_processed()

    def reverse(self):
        """
        page 57
        """
        assert self.is_processed
        for entry in tuple(self._resulting_entries):
            self.reverse_entry(entry)
            for ev in self._secondary_events:
                ev.reverse()

    def reverse_entry(self, entry):
        reversing_entry = Entry(-entry.amount, entry.entry_date, entry_type=entry.entry_type )
        target_account = self._subject.account_for(entry.entry_type)
        target_account.post(reversing_entry)

    def _reverse_secondary_events(self):
        """
        page 57
        """
        [event.reverse() for event in self._secondary_events]

    def friend_add_secondary_event(self, arg):
        """
        page 36
        """
        # only to be caled by the secondary event's setting method
        self._secondary_events.append(arg)

    def get_all_resulting_entries(self):
        """
        page 36
        """
        result = self._resulting_entries
        for event in self._secondary_events:
            result += event.resulting_entries
        return result

    # from page 66
    def set_replacement_event(self, arg):
        self.replacement_event = arg

    def undo(self):
        """
        from page 71, replacement adjustment (remove old, add new)
        """
        for entry in self._resulting_entries:
            self.subject.remove_entry(entry)
        self.undo_secondary_events()
        self._resulting_entries = None

    def undo_secondary_events(self):
        """
        from page 71, replacement adjustment (remove old, add new)
        """
        for event in self._secondary_events:
            event.undo()



class EventList(object):
    """
    see http://martinfowler.com/eaaDev/AgreementDispatcher.html
    """

    def __init__(self):
        self.events = []

    def add(self, event):
        self.events.append(event)

    def unprocessed_events(self):
        return [e for e in self.events if not e.is_processed]

    def process(self):
        for event in self.unprocessed_events():
            event.process()
