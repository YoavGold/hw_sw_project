#!/usr/bin/env python
"""
Clean benchmark for logging without pyperformance overhead.
Test the performance of logging simple messages.
"""

import io
import logging

# A simple format for parametered logging
FORMAT = 'important: %s'
MESSAGE = 'some important information to be logged'


def truncate_stream(stream):
    stream.seek(0)
    stream.truncate()


def bench_silent(loops, logger, stream):
    """Test silent logging calls (debug level when warning is set)"""
    truncate_stream(stream)
    
    # micro-optimization: use fast local variables
    m = MESSAGE

    for _ in range(loops):
        # repeat 10 times
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)
        logger.debug(m)

    if len(stream.getvalue()) != 0:
        raise ValueError("stream is expected to be empty")


def bench_simple_output(loops, logger, stream):
    """Test simple warning messages"""
    truncate_stream(stream)
    
    # micro-optimization: use fast local variables
    m = MESSAGE

    for _ in range(loops):
        # repeat 10 times
        logger.warning(m)
        logger.warning(m)
        logger.warning(m)
        logger.warning(m)
        logger.warning(m)
        logger.warning(m)
        logger.warning(m)
        logger.warning(m)
        logger.warning(m)
        logger.warning(m)

    lines = stream.getvalue().splitlines()
    if len(lines) != loops * 10:
        raise ValueError("wrong number of lines")


def bench_formatted_output(loops, logger, stream):
    """Test formatted warning messages"""
    truncate_stream(stream)
    
    # micro-optimization: use fast local variables
    fmt = FORMAT
    msg = MESSAGE

    for _ in range(loops):
        # repeat 10 times
        logger.warning(fmt, msg)
        logger.warning(fmt, msg)
        logger.warning(fmt, msg)
        logger.warning(fmt, msg)
        logger.warning(fmt, msg)
        logger.warning(fmt, msg)
        logger.warning(fmt, msg)
        logger.warning(fmt, msg)
        logger.warning(fmt, msg)
        logger.warning(fmt, msg)

    lines = stream.getvalue().splitlines()
    if len(lines) != loops * 10:
        raise ValueError("wrong number of lines")


def main():
    loops = 100
    
    # Setup logging
    stream = io.StringIO()
    handler = logging.StreamHandler(stream=stream)
    logger = logging.getLogger("benchlogger")
    logger.propagate = False
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)
    
    print("Running logging silent benchmark...")
    bench_silent(loops, logger, stream)
    
    print("Running logging simple output benchmark...")
    bench_simple_output(loops, logger, stream)
    
    print("Running logging formatted output benchmark...")
    bench_formatted_output(loops, logger, stream)
    
    print(f"Logging benchmarks completed with {loops} loops")


if __name__ == "__main__":
    main()
