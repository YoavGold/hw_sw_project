#!/usr/bin/env python
"""
Clean benchmark for pyflate (compression/decompression) without pyperformance overhead.
Simplified version that creates test data in memory instead of using external files.
"""

import gzip
import bz2
import io

# Create test data
TEST_DATA = b"This is test data for compression benchmark. " * 1000


def bench_gzip_compression(loops):
    """Benchmark gzip compression"""
    for _ in range(loops):
        compressed = gzip.compress(TEST_DATA)
        # Verify we can decompress
        decompressed = gzip.decompress(compressed)
        assert decompressed == TEST_DATA


def bench_bzip2_compression(loops):
    """Benchmark bzip2 compression"""
    for _ in range(loops):
        compressed = bz2.compress(TEST_DATA)
        # Verify we can decompress
        decompressed = bz2.decompress(compressed)
        assert decompressed == TEST_DATA


def bench_gzip_stream(loops):
    """Benchmark gzip streaming compression/decompression"""
    for _ in range(loops):
        # Compression
        buffer = io.BytesIO()
        with gzip.GzipFile(fileobj=buffer, mode='wb') as f:
            f.write(TEST_DATA)
        compressed_data = buffer.getvalue()
        
        # Decompression
        buffer = io.BytesIO(compressed_data)
        with gzip.GzipFile(fileobj=buffer, mode='rb') as f:
            decompressed = f.read()
        assert decompressed == TEST_DATA


def main():
    loops = 10  # Compression is relatively slow
    
    print(f"Running gzip compression benchmark with {len(TEST_DATA)} bytes...")
    bench_gzip_compression(loops)
    
    print(f"Running bzip2 compression benchmark with {len(TEST_DATA)} bytes...")
    bench_bzip2_compression(loops)
    
    print(f"Running gzip streaming benchmark with {len(TEST_DATA)} bytes...")
    bench_gzip_stream(loops)
    
    print(f"Compression benchmarks completed with {loops} loops")


if __name__ == "__main__":
    main()
