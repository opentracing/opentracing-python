# Copyright (c) 2016 The OpenTracing Authors.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
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

    def test_attribute_check_works(self):
        api_check = APICompatibilityCheckMixin()
        setattr(api_check, 'tracer', lambda: Tracer())
        # no-op tracer does not store attributes, so the test with default
        # value of `check_trace_attribute_values()` should fail.
        with self.assertRaises(AssertionError):
            api_check.test_baggage()
