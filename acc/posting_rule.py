from acc.entry import Entry


class PostingRule(object):
    """
    Page 24
    """
    def __init__(self, entry_type):
        self.entry_type = entry_type
        #self.effectivity = None

    def make_entry(self, evt, amount):
        new_entry = Entry(amount, evt.notified_at,
                          entry_type=self.entry_type)
        evt.subject.add_entry(new_entry, self.entry_type)
        evt.add_resulting_entry(new_entry)

    def process(self, event):
        """ sample implementation of process() """
        self.make_entry(event, self.calculate_amount(event))
        #raise NotImplemented("process() not implemented")

    #def calculate_amount(self, evt):
    #    raise NotImplemented
