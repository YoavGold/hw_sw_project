#!/usr/bin/env python
"""
Clean benchmark for crypto_pyaes without pyperformance overhead.
Pure-Python Implementation of the AES block-cipher using pyaes module.
"""

import pyaes

# 23,000 bytes
CLEARTEXT = b"This is a test. What could possibly go wrong? " * 500

# 128-bit key (16 bytes)
KEY = b'\xa1\xf6%\x8c\x87}_\xcd\x89dHE8\xbf\xc9,'


def bench_pyaes(loops):
    for _ in range(loops):
        aes = pyaes.AESModeOfOperationCTR(KEY)
        ciphertext = aes.encrypt(CLEARTEXT)

        # need to reset IV for decryption
        aes = pyaes.AESModeOfOperationCTR(KEY)
        plaintext = aes.decrypt(ciphertext)

        # explicitly destroy the pyaes object
        aes = None

    # Verify correctness
    if plaintext != CLEARTEXT:
        raise Exception("decrypt error!")


def main():
    loops = 100
    bench_pyaes(loops)
    print(f"Crypto pyaes benchmark completed with {loops} loops")


if __name__ == "__main__":
    main()
