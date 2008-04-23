"""
cellulose.restrictions
Copyright 2006 by Matthew Marshall <matthew@matthewmarshall.org>

This module contains classes for restricting InputCells and ComputedCells to
certain sets of values.  (e.g., only strings, or only real numbers between 1.0
and 100.0)

Not a lot thought went into this.  For now at least it works for abstrui.  I'm
open to suggestions for this.

Right now probably the biggest thing that might need to be rethought is the way
it adjusts values to fit the restriction.  For example, if you assign a string
to a cell with a DecimalRestriction, it will automatically try to convert it to
a Decimal, only raising an exception if the string cannot be converted.  This
is the type of behavior you would want for an input field in a UI, but in
general it might not be appropriate.

"""

from cellulose import AutoCells, CellSet
from decimal import Decimal

class RestrictionError(Exception):
    pass

class Restriction(object):
    def test(self, value):
        """
        Test if the value fits with the restriction.  Raise RestrictionError if
        not.
        """
        pass

    def adjust(self,value):
        """
        Return the value, adjusted to fit the restriction.  Raise
        RestrictionError if the value cannot be adjusted.
        """
        test(value)
        return value

class BooleanRestriction(Restriction):
    def test(self, value):
        if value not in (True, False):
            raise RestrictionError
    def adjust(self, value):
        return bool(value)

class DecimalRestriction(Restriction):
    def test(self, value):
        try:
            Decimal(str(value))
        except:
            raise RestrictionError

    def adjust(self, value):
        try:
            return Decimal(str(value))
        except:
            raise RestrictionError

class DecimalRangeRestriction(DecimalRestriction, AutoCells):
    def __init__(self, min=None, max=None):
        Restriction.__init__(self)
        AutoCells.__init__(self)
        self.max = max
        self.min = min

    def test(self, value):
        DecimalRestriction.test(self, value)
        if self.max is not None and value > self.max:
            raise RestrictionError
        if self.min is not None and value < self.min:
            raise RestrictionError

    def adjust(self, value):
        value = DecimalRestriction.adjust(self, value)
        return max(self.min, min(self.max, value))

class StringRestriction(Restriction):
    def test(self, value):
        if not isinstance(value, basestring): # Should I force unicode here?
            raise RestrictionError
    def adjust(self, value):
        return unicode(value)

class StringLengthRestriction(StringRestriction, AutoCells):
    def __init__(self, min=None, max=None):
        StringRestriction.__init__(self)
        AutoCells.__init__(self)
        self.max = max
        self.min = min  # I'm not sure that there is even a use for this :P

    def test(self,value):
        StringRestriction.test(self, value)
        if self.max is not None and len(value) > self.max:
            raise RestrictionError
        if self.min is not None and len(value) < self.min:
            raise RestrictionError

    def adjust(self, value):
        value = StringRestriction.adjust(self, value)
        value = value[:self.max]
        if len(value) < self.min:
            raise RestrictionError # Should this be padded with spaces instead?
        return value


class RestrictionSet(Restriction, CellSet):
    """ A set of other restrictions

    I am not sure wether or not this should be used, as it makes restriction
    introspection more difficult.

    Subclassing, possibly with multiple inheritance, is probably a better
    method.
    """

    def test(self, value):
        for r in self:
            r.test(value)

    def adjust(self, value):
        for r in self:
            new = r.adjust(value)
            if new is not value:
                return self.adjust(new)
        return value
