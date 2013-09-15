from acc.utils import TemporalCollection


class Agreement(object):
    def __init__(self):
        self.posting_rules = {}

    def add_posting_rule(self, event_type, posting_rule, date):
        self.posting_rules.setdefault(event_type, TemporalCollection())
        self.temporal_collection(event_type).put(date, posting_rule)

    def get_posting_rule(self, event_type, when):
        return self.temporal_collection(event_type).get(when)

    def temporal_collection(self, event_type):
        return self.posting_rules.get(event_type)
