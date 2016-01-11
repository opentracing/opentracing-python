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
from example.zipkin_like import Tracer, ConstSampler
from example.zipkin_like.reporter import NullReporter
from example.zipkin_like.context import TraceContextSource
from opentracing.harness.api_check import APICompatibilityCheckMixin


class APICheckZipkinTracer(unittest.TestCase, APICompatibilityCheckMixin):
    sampler = ConstSampler(True)
    source = TraceContextSource(sampler)
    reporter = NullReporter()
    _tracer = Tracer(service_name='api-test',
                     reporter=reporter,
                     trace_context_source=source)

    def tracer(self):
        return APICheckZipkinTracer._tracer

    def test_binary_codecs(self):
        # TODO binary codecs are not implemented at the moment
        pass
