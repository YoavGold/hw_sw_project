#!/usr/bin/env python
"""
Clean benchmark for deepcopy without pyperformance overhead.
Benchmark copy.deepcopy on various data structures.
"""

import copy
from dataclasses import dataclass


@dataclass
class A:
    string: str
    lst: list
    boolean: bool


def benchmark_reduce(loops):
    """ Benchmark where the __reduce__ functionality is used """
    class C(object):
        def __init__(self):
            self.a = 1
            self.b = 2

        def __reduce__(self):
            return (C, (), self.__dict__)

        def __setstate__(self, state):
            self.__dict__.update(state)
    
    c = C()
    for _ in range(loops):
        _ = copy.deepcopy(c)


def benchmark_memo(loops):
    """ Benchmark where the memo functionality is used """
    A = [1] * 100
    data = {'a': (A, A, A), 'b': [A] * 100}

    for _ in range(loops):
        _ = copy.deepcopy(data)


def benchmark_standard(loops):
    """ Benchmark on some standard data types """
    a = {
        'list': [1, 2, 3, 43],
        't': (1, 2, 3),
        'str': 'hello',
        'subdict': {'a': True}
    }
    dc = A('hello', [1, 2, 3], True)

    for _ in range(loops):
        for _ in range(30):
            _ = copy.deepcopy(a)
        for s in ['red', 'blue', 'green']:
            dc.string = s
            for kk in range(5):
                dc.lst[0] = kk
                for b in [True, False]:
                    dc.boolean = b
                    _ = copy.deepcopy(dc)


def main():
    loops = 100
    
    print("Running deepcopy standard benchmark...")
    benchmark_standard(loops)
    
    print("Running deepcopy reduce benchmark...")
    benchmark_reduce(loops * 10)
    
    print("Running deepcopy memo benchmark...")
    benchmark_memo(loops * 10)
    
    print(f"Deepcopy benchmarks completed with {loops} base loops")


if __name__ == "__main__":
    main()
