# Copyright The OpenTracing Authors

from __future__ import absolute_import
import unittest
from opentracing import Tracer
from opentracing.harness.api_check import APICompatibilityCheckMixin


class APICheckNoopTracer(unittest.TestCase, APICompatibilityCheckMixin):
    """
    Run tests from APICompatibilityCheckMixin against default No-op Tracer.
    """

    def tracer(self):
        return Tracer()

    def check_baggage_values(self):
        return False
