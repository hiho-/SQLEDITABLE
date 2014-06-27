# coding: utf8
# try something like
from gluon.custom_import import track_changes; track_changes(True)
from editable import *

def doctest_header():
    '''
    >>> head = [{'default': '', 'field': 'test1', 'readable': False, 'type': 'string', 'writable': False},
    ... {'default': 0, 'field': 'test2', 'readable': True, 'type': 'integer', 'writable': False, 'label': 'TEST2'},
    ... {'default': '', 'field': 'test3', 'length': [0, 512], 'readable': True, 'type': 'string', 'writable': True},
    ... {'field': 'test4', 'readable': True, 'type': 'date', 'writable': False},
    ... {'default': False, 'field': 'test5', 'readable': True, 'type': 'boolean', 'writable': True},
    ... {'default': '', 'field': 'test6', 'readable': True, 'type': 'string', 'writable': True, 'inset':{'multiple':True, 'zero': 'val1', 'theset':['val1','val2','val3']}}]
    >>> header = Header(head, ['test1','test2'])
    >>> header.test1.name
    'test1'
    >>> header['test1'].name
    'test1'
    >>> header.test1.type
    'string'
    >>> header.test1.writable
    False
    >>> header.test1.label
    'test1'
    >>> header.test2['label']
    'TEST2'
    >>> header.test1.has_attr('label')
    False
    >>> header.test4.default
    ''
    >>> header.test5.default
    False
    >>> for k in header.key():
    ...     print k.name
    test1
    test2
    >>> value = [100,150]
    >>> for k, v in zip(header.key(),value):
    ...     print k.name,v
    test1 100
    test2 150
    >>> header.test1.is_key()
    True
    >>> header.test3.is_key()
    False
    >>> header.test6.has_attr('inset')
    True
    >>> header.test6.has_attr('inset.multiple')
    True
    '''
    pass

def doctest_record():
    '''
    >>> import datetime
    >>> head = [{'default': '', 'field': 'test1', 'readable': False, 'type': 'string', 'writable': False},
    ... {'default': 0, 'field': 'test2', 'readable': True, 'type': 'integer', 'writable': False},
    ... {'default': '', 'field': 'test3', 'length': [0, 512], 'readable': True, 'type': 'string', 'writable': True},
    ... {'default': '', 'field': 'test4', 'readable': True, 'type': 'date', 'writable': False},
    ... {'default': False, 'field': 'test5', 'readable': True, 'type': 'boolean', 'writable': True}]
    >>> data = {'test1': 849L, 'test3': 'xxxx1', 'test2': 2L, 'test4': datetime.date(2008, 2, 5), 'test5': False}
    >>> record = Record(data, head, ['test1','test2'])
    >>> 'test1' in data
    True
    >>> p_test = 'test1'
    >>> record.has_field(p_test)
    True
    >>> record.has_field('test20')
    False
    >>> print record.test20
    None
    >>> print record['test1']
    849
    >>> del record['test1']
    >>> del record['test20']    #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    KeyError: 'test20'
    >>> print record.test1
    None
    >>> print record.key_list()
    ['test1', 'test2']
    '''
    pass

def doctest_recordarray():
    '''
    >>> import datetime
    >>> head = [{'default': '', 'field': 'test1', 'readable': False, 'type': 'string', 'writable': False},
    ... {'default': 0, 'field': 'test2', 'readable': True, 'type': 'integer', 'writable': False},
    ... {'default': '', 'field': 'test3', 'length': [0, 512], 'readable': True, 'type': 'string', 'writable': True},
    ... {'default': '', 'field': 'test4', 'readable': True, 'type': 'date', 'writable': False},
    ... {'default': False, 'field': 'test5', 'readable': True, 'type': 'boolean', 'writable': True}]
    >>> data = [{'test1': 849L, 'test3': 'xxxx1', 'test2': 2L, 'test4': datetime.date(2008, 2, 5), 'test5': False},
    ... {'test1': 99L, 'test3': 'xxxx2', 'test2': 5L, 'test4': datetime.date(2010, 12, 12), 'test5': True},
    ... {'test1': 112L, 'test3': 'xxxx3', 'test2': 10L, 'test4': datetime.date(2003, 8, 9), 'test5': False},
    ... {'test1': 333L, 'test3': 'xxxx4', 'test2': 33L, 'test4': datetime.date(1960, 5, 30), 'test5': False}]
    >>> array = RecordArray(data, head, ['test1','test2'])
    >>> for r in array:
    ...     for f,v in r.all():
    ...         print f.name,v
    ...     break
    test1 849
    test2 2
    test3 xxxx1
    test4 2008-02-05
    test5 False
    >>> for r in array:
    ...     for f,v in r.readable():
    ...         print f.name,v
    ...     break
    test2 2
    test3 xxxx1
    test4 2008-02-05
    test5 False
    >>> for r in array:
    ...     for f,v in r.writable():
    ...         print f.name,v
    ...     break
    test3 xxxx1
    test5 False
    >>> for rec in array:
    ...     rec['test3'] = 'changed!'
    ...     rec.test20 = 'new!'
    >>> for rec in array:
    ...     print rec
    {'test1': 849L, 'test3': 'changed!', 'test2': 2L, 'test20': 'new!', 'test4': datetime.date(2008, 2, 5), 'test5': False}
    {'test1': 99L, 'test3': 'changed!', 'test2': 5L, 'test20': 'new!', 'test4': datetime.date(2010, 12, 12), 'test5': True}
    {'test1': 112L, 'test3': 'changed!', 'test2': 10L, 'test20': 'new!', 'test4': datetime.date(2003, 8, 9), 'test5': False}
    {'test1': 333L, 'test3': 'changed!', 'test2': 33L, 'test20': 'new!', 'test4': datetime.date(1960, 5, 30), 'test5': False}
    >>> for rec in array:
    ...     print dict([(k.name,v) for k,v in rec.key_value()])
    ...     break
    {'test1': 849L, 'test2': 2}
    >>> len(array)
    4
    >>> array[4]    #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    IndexError: list index out of range
    >>> array.append('test')    #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    TypeError: value mast be a Record object.
    >>> array.append(Record(data[0], head))
    >>> print array[4]
    {'test1': 849L, 'test3': 'changed!', 'test2': 2L, 'test20': 'new!', 'test4': datetime.date(2008, 2, 5), 'test5': False}
    >>> for r,rec in enumerate(array):
    ...     print r,rec.test1
    0 849
    1 99
    2 112
    3 333
    4 849
    '''
    pass
