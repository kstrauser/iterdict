#!/usr/bin/env python

"""Ensure that an IterDict behaves exactly like a dict, except where it
shouldn't"""

from iterdict import IterDict

import unittest


class IterDictTest(unittest.TestCase):

    def setUp(self):
        self.testdict = IterDict([('foo', 'v2'), ('bar', 'v3')], foo='v1')

    def test_bigrange(self):
        self.testdict.keys()
        try:
            iterrange = xrange
        except NameError:
            iterrange = range
        self.testdict.update((a, a) for a in iterrange(1000000000))  # Billions
        self.assertEqual(self.testdict[10], 10)

    def test_contains_static(self):
        self.assertTrue('foo' in self.testdict)

    def test_contains_iter(self):
        self.assertTrue('bar' in self.testdict)

    def test_contains_neither(self):
        self.assertFalse('baz' in self.testdict)

    def test_del_static(self):
        del self.testdict['foo']

    def test_del_iter(self):
        del self.testdict['bar']

    def test_del_neither(self):
        self.assertRaises(KeyError, self.testdict.__delitem__, 'baz')

    def test_getitem_static(self):
        self.assertEqual(self.testdict['foo'], 'v1')

    def test_getitem_iter(self):
        self.assertEqual(self.testdict['bar'], 'v3')

    def test_getitem_neither(self):
        self.assertRaises(KeyError, self.testdict.__getitem__, 'baz')

    def test_getitem_afterdelete(self):
        self.testdict['bar'] = 'v4'
        del self.testdict['bar']
        self.assertRaises(KeyError, self.testdict.__getitem__, 'bar')

    def test_len_before_flattening(self):
        self.assertRaises(TypeError, len, self.testdict)

    def test_len_after_flattening(self):
        self.testdict.keys()
        self.assertEqual(len(self.testdict), 2)

    def test_get_static(self):
        self.assertEqual(self.testdict.get('foo'), 'v1')

    def test_get_iter(self):
        self.assertEqual(self.testdict.get('bar'), 'v3')

    def test_get_neither(self):
        self.assertEqual(self.testdict.get('baz', -5), -5)

    def test_iterkeys(self):
        self.assertEqual(set(self.testdict.keys()), set(['foo', 'bar']))

    def test_itervalues(self):
        self.assertEqual(set(self.testdict.values()), set(['v1', 'v3']))

    def test_pop_static(self):
        self.assertEqual(self.testdict.pop('foo'), 'v1')
        self.assertFalse('foo' in self.testdict)

    def test_pop_iter(self):
        self.assertEqual(self.testdict.pop('bar'), 'v3')
        self.assertFalse('bar' in self.testdict)

    def test_pop_neither_default(self):
        self.assertEqual(self.testdict.pop('baz', -1), -1)

    def test_pop_neither_nodefault(self):
        self.assertRaises(KeyError, self.testdict.pop, 'baz')

    def test_popitem_static(self):
        self.assertEqual(self.testdict.popitem('foo'), ('foo', 'v1'))
        self.assertFalse('foo' in self.testdict)

    def test_popitem_iter(self):
        self.assertEqual(self.testdict.popitem('bar'), ('bar', 'v3'))
        self.assertFalse('bar' in self.testdict)

    def test_pop_neither(self):
        self.assertRaises(KeyError, self.testdict.popitem, 'baz')

    def test_setdefault_static(self):
        self.assertEqual(self.testdict.setdefault('foo', 'v4'), 'v1')

    def test_setdefault_iter(self):
        self.assertEqual(self.testdict.setdefault('bar', 'v4'), 'v3')

    def test_setdefault_neither(self):
        self.assertEqual(self.testdict.setdefault('baz', 'v4'), 'v4')
        self.assertEqual(self.testdict['baz'], 'v4')

    def test_update_onlywhenready(self):
        self.assertRaises(ValueError, self.testdict.update, kwargs={'hi': 'lo'})

    def test_update_kw(self):
        self.testdict.keys()
        self.testdict.update(hi='lo')
        self.assertEqual(self.testdict['hi'], 'lo')

    def test_update_dict(self):
        self.testdict.keys()
        self.testdict.update({'hi': 'lo'})
        self.assertEqual(self.testdict['hi'], 'lo')

    def test_update_iter(self):
        self.testdict.keys()
        self.testdict.update([('hi', 'lo')])
        self.assertEqual(self.testdict['hi'], 'lo')

    def test_update_iterdict_static(self):
        self.testdict.keys()
        ld = IterDict(spam='eggs')
        self.testdict.update(ld)
        self.assertEqual(self.testdict['spam'], 'eggs')

    def test_update_iterdict_iter(self):
        self.testdict.keys()
        ld = IterDict({'hi': 'lo'}, spam='eggs')
        self.testdict.update(ld)
        self.assertEqual(self.testdict['hi'], 'lo')

if __name__ == '__main__':
    unittest.main()
