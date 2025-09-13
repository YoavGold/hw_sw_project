#!/usr/bin/env python
"""
Clean benchmark for pathlib without pyperformance overhead.
Test the performance of pathlib operations.
"""

import os
import pathlib
import shutil
import tempfile

NUM_FILES = 2000


def generate_filenames(tmp_path, num_files):
    i = 0
    while num_files:
        for ext in [".py", ".txt", ".tar.gz", ""]:
            i += 1
            yield os.path.join(tmp_path, str(i) + ext)
            num_files -= 1


def setup(num_files):
    tmp_path = tempfile.mkdtemp()
    for fn in generate_filenames(tmp_path, num_files):
        with open(fn, "wb") as f:
            f.write(b'benchmark')
    return tmp_path


def bench_pathlib(loops, tmp_path):
    base_path = pathlib.Path(tmp_path)

    # Warm up the filesystem cache and keep some objects in memory.
    path_objects = list(base_path.iterdir())
    # Cache filesystem metadata
    for p in path_objects:
        p.stat()
    assert len(path_objects) == NUM_FILES, len(path_objects)

    for _ in range(loops):
        # Do something simple with each path.
        for p in base_path.iterdir():
            p.stat()
        for p in base_path.glob("*.py"):
            p.stat()
        for p in base_path.iterdir():
            p.stat()
        for p in base_path.glob("*.py"):
            p.stat()


def main():
    loops = 10  # Filesystem operations are relatively slow
    
    tmp_path = setup(NUM_FILES)
    try:
        print(f"Running pathlib benchmark with {NUM_FILES} files...")
        bench_pathlib(loops, tmp_path)
        print(f"Pathlib benchmark completed with {loops} loops")
    finally:
        shutil.rmtree(tmp_path)


if __name__ == "__main__":
    main()
