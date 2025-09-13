#!/usr/bin/env python
"""
Clean benchmark for pickle operations without pyperformance overhead.
Test pickling/unpickling performance on various data structures.
"""

import datetime
import pickle
import random
import sys

# Test data structures
DICT = {
    'ads_flags': 0,
    'age': 18,
    'birthday': datetime.date(1980, 5, 7),
    'bulletin_count': 0,
    'comment_count': 0,
    'country': 'BR',
    'encrypted_id': 'G9urXXAJwjE',
    'favorite_count': 9,
    'first_name': '',
    'flags': 412317970704,
    'friend_count': 0,
    'gender': 'm',
    'gender_for_display': 'Male',
    'id': 302935349,
    'is_custom_profile_icon': 0,
    'last_name': '',
    'locale_preference': 'pt_BR',
    'member': 0,
    'tags': ['a', 'b', 'c', 'd', 'e', 'f', 'g'],
    'profile_foo_id': 827119638,
    'secure_encrypted_id': 'Z_xxx2dYx3t4YAdnmfgyKw',
    'session_number': 2,
    'signup_id': '201-19225-223',
    'status': 'A',
    'theme': 1,
    'time_created': 1225237014,
    'time_updated': 1233134493,
    'unread_message_count': 0,
    'user_group': '0',
    'username': 'collinwinter',
    'play_count': 9,
    'view_count': 7,
    'zip': ''
}

TUPLE = (
    [265867233, 265868503, 265252341, 265243910, 265879514,
     266219766, 266021701, 265843726, 265592821, 265246784,
     265853180, 45526486, 265463699, 265848143, 265863062,
     265392591, 265877490, 265823665, 265828884, 265753032], 60)

LIST = [[list(range(10)), list(range(10))] for _ in range(10)]

MICRO_DICT = dict((key, dict.fromkeys(range(10))) for key in range(100))


def mutate_dict(orig_dict, random_source):
    new_dict = dict(orig_dict)
    for key, value in new_dict.items():
        rand_val = random_source.random() * sys.maxsize
        if isinstance(key, (int, bytes, str)):
            new_dict[key] = type(key)(rand_val)
    return new_dict


# Create test data
random_source = random.Random(5)  # Fixed seed
DICT_GROUP = [mutate_dict(DICT, random_source) for _ in range(3)]


def bench_pickle(loops, protocol=pickle.HIGHEST_PROTOCOL):
    """Benchmark pickle.dumps() on various objects"""
    dumps = pickle.dumps
    objs = (DICT, TUPLE, DICT_GROUP)

    for _ in range(loops):
        for obj in objs:
            # 20 dumps per object
            for _ in range(20):
                dumps(obj, protocol)


def bench_unpickle(loops, protocol=pickle.HIGHEST_PROTOCOL):
    """Benchmark pickle.loads() on various objects"""
    # Pre-pickle the objects
    pickled_dict = pickle.dumps(DICT, protocol)
    pickled_tuple = pickle.dumps(TUPLE, protocol)
    pickled_dict_group = pickle.dumps(DICT_GROUP, protocol)
    
    loads = pickle.loads
    objs = (pickled_dict, pickled_tuple, pickled_dict_group)

    for _ in range(loops):
        for obj in objs:
            # 20 loads per object
            for _ in range(20):
                loads(obj)


def bench_pickle_list(loops, protocol=pickle.HIGHEST_PROTOCOL):
    """Benchmark pickling lists"""
    dumps = pickle.dumps
    obj = LIST

    for _ in range(loops):
        # 10 dumps per loop
        for _ in range(10):
            dumps(obj, protocol)


def bench_unpickle_list(loops, protocol=pickle.HIGHEST_PROTOCOL):
    """Benchmark unpickling lists"""
    pickled_list = pickle.dumps(LIST, protocol)
    loads = pickle.loads

    for _ in range(loops):
        # 10 loads per loop
        for _ in range(10):
            loads(pickled_list)


def bench_pickle_dict(loops, protocol=pickle.HIGHEST_PROTOCOL):
    """Benchmark pickling dictionaries"""
    dumps = pickle.dumps
    obj = MICRO_DICT

    for _ in range(loops):
        # 5 dumps per loop
        for _ in range(5):
            dumps(obj, protocol)


def main():
    loops = 100
    protocol = pickle.HIGHEST_PROTOCOL
    
    print("Running pickle benchmark...")
    bench_pickle(loops, protocol)
    
    print("Running unpickle benchmark...")
    bench_unpickle(loops, protocol)
    
    print("Running pickle list benchmark...")
    bench_pickle_list(loops, protocol)
    
    print("Running unpickle list benchmark...")
    bench_unpickle_list(loops, protocol)
    
    print("Running pickle dict benchmark...")
    bench_pickle_dict(loops, protocol)
    
    print(f"Pickle benchmarks completed with {loops} loops")


if __name__ == "__main__":
    main()
