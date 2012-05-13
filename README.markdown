# Haven't you always wanted an infinite dict?

IterDicts are similar to regular Python dicts except that they're only
populated upon demand. This gives them most of the same advantages of
generators, such as the ability to operator on very large (or infinite!)
datasets.

## Accessing keys that aren't populated yet

When the `get` or `__getitem__` methods are called, an IterDict tries to
fetch a key in the normal manner. If that fails, it starts consuming the
iterator it was constructed with and adding those items to itself until
it finds the key (or the universe dies of heat death):

	>>> d = IterDict((a, a) for a in xrange(1000000000000000))  # 1 quadrillion (US)
	>>> d[10]
	10

    >>> list(d)
    [you're going to be here a while]

## Important differences

A dict consumes its iterator at initialization, and in the case of duplicates
the last value wins:

    >>> d = dict([(1,1),(1,2)])
    >>> d
    {1: 2}
    >>> del d[1]
    >>> d
    {}

IterDicts differ in that they stop consuming their iterators as soon as the
first instance of a requested key is found:

    >>> i = IterDict([(1,1), (1,2)])
    >>> i
    IterDict<{}, fed by <listiterator object at 0x105bab8d0>>
    >>> i[1]
    1
    >>> i
    IterDict<{1: 1}, fed by <listiterator object at 0x105bab8d0>>

For space, time, and complexity reasons, IterDicts don't track keys that were
present at one point and have been since deleted. This means that keys may
reappear after deletion if the IterDict's iterator yields them again.
Continuing the previous example:

    >>> del i[1]
    >>> i
    IterDict<{}, fed by <listiterator object at 0x105bab890>>
    >>> i[1]
    2
    >>> i
    IterDict<{1: 2}, fed by <listiterator object at 0x105bab890>>

