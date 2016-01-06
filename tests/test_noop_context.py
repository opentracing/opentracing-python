# Copyright (c) 2015 Uber Technologies, Inc.
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
from opentracing import TraceContext, TraceContextSource
from opentracing import TraceContextEncoder, TraceContextDecoder


def test_context():
    ctx = TraceContext()
    assert ctx.get_trace_attribute('x') is None
    ctx.set_trace_attribute('X_y', 'value').\
        set_trace_attribute('ZZ', 'value2')
    assert ctx.get_trace_attribute('X_y') is None


def test_context_source():
    singleton = TraceContextSource.singleton_noop_trace_context
    source = TraceContextSource()
    assert source.new_root_trace_context() == singleton
    child, attr = source.new_child_trace_context(
        parent_trace_context=singleton)
    assert child == singleton
    assert attr is None


def test_encoder():
    singleton = TraceContextSource.singleton_noop_trace_context
    e = TraceContextEncoder()
    x, y = e.trace_context_to_binary(trace_context=singleton)
    assert x == bytearray()
    assert y is None
    x, y = e.trace_context_to_text(trace_context=singleton)
    assert x == {}
    assert y is None


def test_decoder():
    singleton = TraceContextSource.singleton_noop_trace_context
    d = TraceContextDecoder()
    ctx = d.trace_context_from_binary(trace_context_id=None,
                                      trace_attributes=None)
    assert singleton == ctx
    ctx = d.trace_context_from_text(trace_context_id=None,
                                    trace_attributes=None)
    assert singleton == ctx
