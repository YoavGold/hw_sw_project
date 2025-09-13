#!/usr/bin/env python
"""
Clean benchmark for json.dumps() without pyperformance overhead.
Tests JSON serialization performance on various data structures.
"""

import json

# Test data
EMPTY = ({}, 2000)
SIMPLE_DATA = {'key1': 0, 'key2': True, 'key3': 'value', 'key4': 'foo',
               'key5': 'string'}
SIMPLE = (SIMPLE_DATA, 1000)
NESTED_DATA = {'key1': 0, 'key2': SIMPLE[0], 'key3': 'value', 'key4': SIMPLE[0],
               'key5': SIMPLE[0], 'key': '\u0105\u0107\u017c'}
NESTED = (NESTED_DATA, 1000)
HUGE = ([NESTED[0]] * 1000, 1)

CASES = ['EMPTY', 'SIMPLE', 'NESTED', 'HUGE']


def bench_json_dumps(data):
    """Core JSON dumps benchmark"""
    for obj, count_it in data:
        for _ in count_it:
            json.dumps(obj)


def main():
    print("Running JSON dumps benchmark...")
    
    # Prepare data similar to the original benchmark
    data = []
    for case in CASES:
        obj, count = globals()[case]
        data.append((obj, range(count)))
    
    bench_json_dumps(data)
    print("JSON dumps benchmark completed")


if __name__ == '__main__':
    main()
