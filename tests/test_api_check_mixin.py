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

    def test_default_scope_manager_check_mode(self):
        api_check = APICompatibilityCheckMixin()
        assert api_check.check_scope_manager() is True

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

    def test_scope_manager_check_works(self):
        api_check = APICompatibilityCheckMixin()
        setattr(api_check, 'tracer', lambda: Tracer())

        # these tests are expected to succeed
        api_check.test_start_active_ignore_active_scope()
        api_check.test_start_manual_propagation_ignore_active_scope()

        # no-op tracer doesn't have a ScopeManager implementation
        # so these tests are expected to work, but asserts to fail
        with self.assertRaises(AssertionError):
            api_check.test_start_active()

        with self.assertRaises(AssertionError):
            api_check.test_start_active_parent()

        with self.assertRaises(AssertionError):
            api_check.test_start_active_finish_on_close()

        with self.assertRaises(AssertionError):
            api_check.test_start_manual_propagation()

        with self.assertRaises(AssertionError):
            api_check.test_tracer_start_active_scope()

        with self.assertRaises(AssertionError):
            api_check.test_tracer_start_active_nesting()

        with self.assertRaises(AssertionError):
            api_check.test_tracer_start_active_nesting_finish_on_close()

        with self.assertRaises(AssertionError):
            api_check.test_tracer_start_active_wrong_close_order()

        with self.assertRaises(AssertionError):
            api_check.test_tracer_start_manual_scope()

        with self.assertRaises(AssertionError):
            api_check.test_tracer_scope_manager_active()

        with self.assertRaises(AssertionError):
            api_check.test_tracer_scope_manager_activate()
