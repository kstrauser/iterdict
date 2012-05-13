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

__all__ = ['IterDict']


def _clonedictmethod(func):
    """Copy docstrings from dict methods to the iterdict method with the same
    name"""
    # Python 3 dicts don't have all the same attributes as Python 2's dicts.
    # In this context, that's not a big deal; just ignore it.
    try:
        newdoc = getattr(dict, func.__name__).__doc__
    except AttributeError:
        return func
    olddoc = func.__doc__
    if olddoc:
        func.__doc__ = newdoc + '\n\n' + olddoc
    else:
        func.__doc__ = newdoc
    return func


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

    @_clonedictmethod
    def __init__(self, *args, **kwargs):
        super(IterDict, self).__init__()

        # This tracks the passed-in iterator used to fill in keys as they're
        # requested.
        self.__iterator = None

        try:
            self.__iterkeys = super(IterDict, self).iterkeys
        except AttributeError:
            self.__iterkeys = super(IterDict, self).keys
        try:
            self.__itervalues = super(IterDict, self).itervalues
        except AttributeError:
            self.__itervalues = super(IterDict, self).values
        try:
            self.__iteritems = super(IterDict, self).iteritems
        except AttributeError:
            self.__iteritems = super(IterDict, self).items
        self.update(*args, **kwargs)

    def __processiter(self):
        """yield all of the values in self.__iterator until it's exhausted,
        then mark it as such"""
        if self.__iterator is None:
            raise StopIteration
        for key, value in self.__iterator:
                self[key] = value
                yield key, value
        self.__iterator = None

    @_clonedictmethod
    def __contains__(self, searchkey):
        if super(IterDict, self).__contains__(searchkey):
            return True
        for key, value in self.__processiter():  # pylint: disable=W0612
            if key == searchkey:
                return True
        return False

    @_clonedictmethod
    def __delitem__(self, searchkey):
        try:
            super(IterDict, self).__delitem__(searchkey)
        except KeyError:
            for key, value in self.__processiter():  # pylint: disable=W0612
                if key == searchkey:
                    break
            else:
                raise KeyError(searchkey)

    @_clonedictmethod
    def __getitem__(self, searchkey):
        try:
            return super(IterDict, self).__getitem__(searchkey)
        except KeyError:
            pass
        for key, value in self.__processiter():
            if key == searchkey:
                return value
        raise KeyError(searchkey)

    @_clonedictmethod
    def __len__(self):
        """Note: __len__ is only defined for iterdicts whose iterators have
        already been consumed. Otherwise, there's no way to tell how long those
        iterators may turn out to be. Imagine 1,000 copies of ('key', 'value')
        where 'key' can only be a dict key one time, not 1,000 times."""
        if self.__iterator is None:
            return super(IterDict, self).__len__()
        raise TypeError("objects of type 'iterdict' sometimes have no defined len()")

    @_clonedictmethod
    def __repr__(self):
        if self.__iterator is None:
            return super(IterDict, self).__repr__()
        return 'IterDict<%s, fed by %s>' % (super(IterDict, self).__repr__(),
            repr(self.__iterator))

    @_clonedictmethod
    def __setitem__(self, key, value):
        if not super(IterDict, self).__contains__(key):
            super(IterDict, self).__setitem__(key, value)

    #### Standard dict methods

    @_clonedictmethod
    def get(self, searchkey, default=None):
        try:
            return self.__getitem__(searchkey)
        except KeyError:
            return default

    has_key = __contains__

    @_clonedictmethod
    def iterkeys(self):
        for key, value in self.iteritems():
            yield key

    __iter__ = iterkeys

    @_clonedictmethod
    def items(self):
        return list(self.iteritems())

    @_clonedictmethod
    def itervalues(self):
        for key, value in self.iteritems():
            yield value

    @_clonedictmethod
    def iteritems(self):
        for item in self.__iteritems():
            yield item
        for key, value in self.__processiter():
            if not self.__contains__(key):  # FIXME
                yield (key, value)
            else:
                print 'Already yielded', key

    @_clonedictmethod
    def keys(self):
        """Note: This attempts to cast a potentially infinite generator to a
        list. That is not guaranteed to work in finite time and space."""
        return list(self.iterkeys())

    @_clonedictmethod
    def pop(self, searchkey, default=None):
        try:
            value = self.__getitem__(searchkey)
            del self[searchkey]
            return value
        except KeyError:
            if default is not None:
                return default
            raise

    @_clonedictmethod
    def popitem(self, searchkey):
        value = self.__getitem__(searchkey)
        del self[searchkey]
        return (searchkey, value)

    @_clonedictmethod
    def setdefault(self, searchkey, default):
        try:
            return self.__getitem__(searchkey)
        except KeyError:
            self[searchkey] = default
            return default

    @_clonedictmethod
    def update(self, iterator=None, **kwargs):
        if not self.__iterator is None:
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

    @_clonedictmethod
    def values(self):
        """Note: This attempts to cast a potentially infinite generator to a
        list. That is not guaranteed to work in finite time and space."""
        return list(self.itervalues())
