#!/usr/bin/env python

# Copyright (c) 2012, Kirk Strauser <kirk@strauser.com>
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


"""Define a IterDict class which lazily evaluates initialization objects passed
into it"""

import sys
from functools import wraps

__all__ = ['IterDict']


@wraps(wraps)
def dictmethod(wrapped):
    """Specialization of functools.wraps that skips the __module__ attribute
    (which dict objects don't have)"""
    from functools import WRAPPER_ASSIGNMENTS
    wr_ass = set(WRAPPER_ASSIGNMENTS)
    wr_ass.remove('__module__')
    return wraps(wrapped, wr_ass)


def findkeybeforedictmethod(func):
    """Search for the key given in args[0] before calling the wrapped
    function"""
    @dictmethod(func)
    def inner(self, *args, **kwargs):
        """Find that key first!"""
        args[0] in self  # pylint: disable=W0104
        return func(self, *args, **kwargs)
    return inner


class IterDict(dict):
    """IterDicts are dicts at heart and behave almost identically, with the
    exception that they can be initialized with large or infinite iterators and
    use lazy evaluation to avoid resolving keys until those keys are actually
    referenced. As new items from the iterator are processed, they are added
    into the dict as usually.

    Note: since iterator processing is deferred as long as possible, it respects
    keys that have been already added to or deleted from the dict. That is,
    it won't overwrite a key present in the dict, and it won't create a key if
    that key has already been deleted from the dict. Surprises are bad."""

    if sys.version_info[0] == 2:
        __iteritems = dict.iteritems
        __iterkeys = dict.iterkeys
        __itervalues = dict.itervalues
    else:
        __iteritems = dict.items
        __iterkeys = dict.keys
        __itervalues = dict.values

    @dictmethod(dict.__init__)
    def __init__(self, *args, **kwargs):
        super(IterDict, self).__init__()

        # This tracks the passed-in iterator used to fill in keys as they're
        # requested.
        self.__iterator = None

        self.update(*args, **kwargs)

    @dictmethod(dict.__contains__)
    def __contains__(self, searchkey):
        if super(IterDict, self).__contains__(searchkey):
            return True
        if self.__iterator is None:
            return False
        for key, value in self.__iterator:
            if not super(IterDict, self).__contains__(key):
                super(IterDict, self).__setitem__(key, value)
            if key == searchkey:
                return True
        return False

    def __missing__(self, searchkey):
        if searchkey in self:
            return self[searchkey]
        else:
            raise KeyError(searchkey)

    @dictmethod(dict.__len__)
    def __len__(self):
        """Note: __len__ is only defined for iterdicts whose iterators have
        already been consumed. Otherwise, there's no way to tell how long those
        iterators may turn out to be. Imagine 1,000 copies of ('key', 'value')
        where 'key' can only be a dict key one time, not 1,000 times."""
        if self.__iterator is None:
            return super(IterDict, self).__len__()
        raise TypeError("objects of type 'IterDict' sometimes have no defined len()")

    @dictmethod(dict.__repr__)
    def __repr__(self):
        if self.__iterator is None:
            return super(IterDict, self).__repr__()
        return 'IterDict<%s, fed by %s>' % (super(IterDict, self).__repr__(),
            repr(self.__iterator))

    #### Standard dict methods

    get = findkeybeforedictmethod(dict.get)

    @dictmethod(__iteritems)
    def items(self):
        for item in self.__iteritems():
            yield item
        if self.__iterator is None:
            raise StopIteration
        for key, value in self.__iterator:
            if not super(IterDict, self).__contains__(key):
                super(IterDict, self).__setitem__(key, value)
                yield key, value
        self.__iterator = None

    @dictmethod(__iterkeys)
    def keys(self):
        for key, value in self.items():  # pylint: disable=W0612
            yield key

    @dictmethod(__itervalues)
    def values(self):
        for key, value in self.items():  # pylint: disable=W0612
            yield value

    pop = findkeybeforedictmethod(dict.pop)

    @dictmethod(dict.popitem)
    def popitem(self):
        try:
            return super(IterDict, self).popitem()
        except KeyError:
            if self.__iterator is None:
                raise KeyError('popitem(): dictionary is empty')
            for key, value in self.__iterator:
                if not super(IterDict, self).__contains__(key):
                    return key, value
            self.__iterator = None
            raise KeyError('popitem(): dictionary is empty')

    setdefault = findkeybeforedictmethod(dict.setdefault)

    @dictmethod(dict.update)
    def update(self, iterator=None, **kwargs):
        if self.__iterator is not None:
            raise ValueError('The current iterator is not yet exhausted')
        super(IterDict, self).update(**kwargs)
        if iterator is None:
            pass
        elif type(iterator) == dict:
            super(IterDict, self).update(iterator)
        elif hasattr(iterator, '__iter__'):
            try:
                self.__iterator = iterator.iteritems()
            except AttributeError:
                try:
                    self.__iterator = iterator.items()
                except AttributeError:
                    self.__iterator = iter(iterator)
        else:
            raise ValueError('%s is not iterable' % repr(iterator))

    #### IterDict-specific

    def flatten(self):
        """Update the IterDict with all keys from the iterator"""
        for key, value in self.items():  # pylint: disable=W0612
            pass
