#!/usr/bin/env python
"""
Clean benchmark for sequence unpacking without pyperformance overhead.
Microbenchmark for Python's tuple and list unpacking performance.
"""


def do_unpacking(loops, to_unpack):
    """Core unpacking benchmark - performs 400 unpackings per loop"""
    for _ in range(loops):
        # 400 unpackings per loop
        for _ in range(40):
            a, b, c, d, e, f, g, h, i, j = to_unpack
            a, b, c, d, e, f, g, h, i, j = to_unpack
            a, b, c, d, e, f, g, h, i, j = to_unpack
            a, b, c, d, e, f, g, h, i, j = to_unpack
            a, b, c, d, e, f, g, h, i, j = to_unpack
            a, b, c, d, e, f, g, h, i, j = to_unpack
            a, b, c, d, e, f, g, h, i, j = to_unpack
            a, b, c, d, e, f, g, h, i, j = to_unpack
            a, b, c, d, e, f, g, h, i, j = to_unpack
            a, b, c, d, e, f, g, h, i, j = to_unpack


def bench_tuple_unpacking(loops):
    """Benchmark tuple unpacking"""
    x = tuple(range(10))
    do_unpacking(loops, x)


def bench_list_unpacking(loops):
    """Benchmark list unpacking"""
    x = list(range(10))
    do_unpacking(loops, x)


def bench_all(loops):
    """Benchmark both tuple and list unpacking"""
    bench_tuple_unpacking(loops)
    bench_list_unpacking(loops)


def main():
    loops = 100
    
    print("Running tuple unpacking benchmark...")
    bench_tuple_unpacking(loops)
    
    print("Running list unpacking benchmark...")
    bench_list_unpacking(loops)
    
    print("Running combined unpacking benchmark...")
    bench_all(loops)
    
    print(f"Unpack sequence benchmarks completed with {loops} loops")


if __name__ == "__main__":
    main()
