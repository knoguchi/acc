import datetime


class O:
    @classmethod
    def values(cls):
        return [v for k, v in cls.__dict__.items() if not k.startswith('_')]


class DateRange:
    EMPTY = None

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def includes(self, date):
        if type(date) != datetime.date:
            return self.start <= date.start and self.end >= date.end
        if self.start:
            if self.end:
                return (self.start <= date) and (date <= self.end)
            else:
                return self.start <= date
        if self.end:
            return date <= self.end
        return False

    @classmethod
    def upto(cls, date):
        return DateRange(None, date)

    def gap(self, arg):
        if self.overlaps(arg):
            return DateRange.EMPTY
        if self < arg:
            lower = self
            higher = arg
        else:
            lower = arg
            higher = self
        return DateRange(lower.end + datetime.timedelta(1),
                         higher.start + datetime.timedelta(-1))

    def overlaps(self, arg):
        return arg.includes(self.start) or arg.includes(
            self.end) or self.includes(arg)

    def abuts(self, arg):
        return not self.overlaps(arg) and self.gap(arg).is_empty()

    def is_empty(self):
        return self.start - self.end == datetime.timedelta(0)

    @classmethod
    def combination(cls, args):
        args.sort()
        if not DateRange.is_contiguous(args):
            raise ValueError("Unable to combine date ranges")
        return DateRange(args[0].start, args[-1].end)

    @classmethod
    def is_contiguous(cls, args):
        args.sort()
        for i in range(len(args) - 1):
            if not args[i].abuts(args[i + 1]):
                return False
        return True

    def __repr__(self):
        return "%s - %s" % (self.start, self.end)


class TemporalCollection:
    def __init__(self):
        self.contents = {}
        self._milestone_cache = None

    def get(self, when):
        """
        returns the value that was effective on the given date
        """
        for milestone in self.milestones():
            if milestone <= when:
                return self.contents.get(milestone)
            #IllegalArgumentException
        raise ValueError("no records that early")

    def put(self, at, item):
        """ the item is valid from the supplied data onwards """
        self.contents[at] = item
        self.clear_milestone_cache()

    def milestones(self):
        """
        a list of all the dates where the value changed,
        returned in order latest first
        """
        if self._milestone_cache is None:
            self.calculate_milestones()
        return self._milestone_cache

    def calculate_milestones(self):
        self._milestone_cache = list(self.contents.keys())
        self._milestone_cache.sort()
        self._milestone_cache.reverse()

    def clear_milestone_cache(self):
        self._milestone_cache = None

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self