# Haven't you always wanted an infinite dict?

IterDicts are almost exactly like regular Python dicts, except that they're
only populated upon demand. This gives them most of the same advantages of
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

## Deleting keys that aren't populated yet

IterDicts also track keys that have been deleted from themselves and ensure
that the iterator can't add those keys back:

	>>> del d[20]
	>>> del d[20]
	KeyError: 20

This is based on the Principal of Least Astonishment. When you delete a key a
regular dict, it doesn't come back. However, an IterDict's iterator may very
well yield a key again later, and we probably don't want that key re-injected
into the dict. That would give strange and surprising results like:

    >>> d = IterDict([(1,1), (2,2), (1,1)])
    >>> del d[1]
    >>> d[2]
    2
    >>> del d[1]
    1  # <- Huh?
