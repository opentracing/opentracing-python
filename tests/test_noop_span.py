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
import mock
from opentracing import Span, TraceContextSource
from opentracing.ext import tags


def test_span():
    ctx = TraceContextSource().new_root_trace_context()
    span = Span(trace_context=ctx)
    assert span.trace_context == ctx
    child = span.start_child(operation_name='test')
    assert span == child
    child.info('cache hit', 'arg1', 'arg2')
    child.error('cache miss', 'arg1', 'arg2')

    with mock.patch.object(span, 'finish') as finish:
        with mock.patch.object(span, 'error') as error:
            try:
                with span:
                    raise ValueError()
            except ValueError:
                pass
            assert finish.call_count == 1
            assert error.call_count == 1

    with mock.patch.object(span, 'finish') as finish:
        with mock.patch.object(span, 'error') as error:
            with span:
                pass
            assert finish.call_count == 1
            assert error.call_count == 0

    span.add_tag('x', 'y').add_tag('z', 1)
    span.add_tag(tags.RPC_TARGET_SERVICE, 'test-service')
    span.add_tag(tags.RPC_HOST_IPV4, 127 << 24 + 1)
    span.add_tag(tags.RPC_HOST_IPV6, '::')
    span.add_tag(tags.RPC_HOSTNAME, 'uber.com')
    span.add_tag(tags.RPC_PORT, 123)
    span.finish()
