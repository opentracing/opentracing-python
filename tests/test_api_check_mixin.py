# Copyright The OpenTracing Authors

from __future__ import absolute_import
import unittest
from opentracing import Tracer
from opentracing.harness.api_check import APICompatibilityCheckMixin


class VerifyAPICompatibilityCheck(unittest.TestCase):
    def test_tracer_exception(self):
        api_check = APICompatibilityCheckMixin()
        with self.assertRaises(NotImplementedError):
            api_check.tracer()

    def test_default_baggage_check_mode(self):
        api_check = APICompatibilityCheckMixin()
        assert api_check.check_baggage_values() is True

    def test_baggage_check_works(self):
        api_check = APICompatibilityCheckMixin()
        setattr(api_check, 'tracer', lambda: Tracer())

        # no-op tracer does not store baggage, so the test with default
        # value of `check_baggage_values()` should fail.
        with self.assertRaises(AssertionError):
            api_check.test_span_baggage()

        # second check that assert on empty baggage will fail too
        with self.assertRaises(AssertionError):
            api_check.test_context_baggage()
