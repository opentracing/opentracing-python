from importlib import import_module
import logging
import os
import six
import unittest


enabled_platforms = [
    'threads',
    'tornado',
    'gevent',
    'flask',
]
if six.PY3:
    enabled_platforms.append('asyncio')

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

unittest.TextTestRunner(verbosity=3).run(main_suite)
