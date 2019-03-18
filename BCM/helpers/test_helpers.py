import sys


def is_test_environment():
    return len(sys.argv) > 1 and sys.argv[1] == 'test'
