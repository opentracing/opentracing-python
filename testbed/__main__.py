from importlib import import_module
import logging
import os
import sys
import six
import unittest
from tornado import version_info as tornado_version


enabled_platforms = [
    'threads',
    'gevent',
]
if tornado_version < (6, 0, 0, 0):
    # Including testbed for Tornado coroutines and stack context.
    # We don't need run testbed in case Tornado>=6, because it became
    # asyncio-based framework and `stack_context` was deprecated.
    enabled_platforms.append('tornado')
if six.PY3:
    enabled_platforms.append('asyncio')
if sys.version_info >= (3, 7):
    enabled_platforms.append('contextvars')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__package__)


def import_test_module(test_name, platform):
    full_path = '%s.%s.test_%s' % (__package__, test_name, platform)
    try:
        return import_module(full_path)
    except ImportError:
        pass

    return None


def get_test_directories():
    """Return all the directories starting with test_ under this package."""
    return [directory for directory in os.listdir(os.path.dirname(__file__))
            if directory.startswith('test_')]


main_suite = unittest.TestSuite()
loader = unittest.TestLoader()

for test_dir in get_test_directories():
    for platform in enabled_platforms:

        test_module = import_test_module(test_dir, platform)
        if test_module is None:
            logger.warning('Could not load %s for %s' % (test_dir, platform))
            continue

        suite = loader.loadTestsFromModule(test_module)
        main_suite.addTests(suite)

result = unittest.TextTestRunner(verbosity=3).run(main_suite)
if result.failures or result.errors:
    sys.exit(1)
