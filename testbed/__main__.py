from importlib import import_module
import six
import unittest

import testbed


enabled_platforms = [
    'threads',
    'tornado',
    'gevent',
]
if six.PY3:
    enabled_platforms.append('asyncio')


def import_test_module(test_name, platform):
    full_path = 'testbed.%s.test_%s' % (test_name, platform)
    try:
        return import_module(full_path)
    except ImportError:
        pass

    return None


if __name__ == '__main__':
    main_suite = unittest.TestSuite()
    loader = unittest.TestLoader()

    for test_name in testbed.TEST_NAMES:
        for platform in enabled_platforms:

            test_module = import_test_module(test_name, platform)
            if test_module is None:
                continue

            suite = loader.loadTestsFromModule(test_module)
            main_suite.addTests(suite)

    unittest.TextTestRunner(verbosity=3).run(main_suite)
