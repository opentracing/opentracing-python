# Copyright (c) 2016 The OpenTracing Authors.
#
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
from opentracing import child_of
from opentracing import Tracer
from opentracing.ext import tags


def test_span():
    tracer = Tracer()
    parent = tracer.start_active_span('parent')
    child = tracer.start_active_span('test',
                                     references=child_of(parent.context))
    assert parent == child

    with mock.patch.object(parent, 'deactivate') as deactivate:
        with mock.patch.object(parent, 'log_event') as log_event:
            with mock.patch.object(parent, 'log_kv') as log_kv:
                try:
                    with parent:
                        raise ValueError()
                except ValueError:
                    pass

                assert deactivate.call_count == 1
                assert log_event.call_count == 0
                assert log_kv.call_count == 1

    with mock.patch.object(parent, 'deactivate') as deactivate:
        with mock.patch.object(parent, 'log_kv') as log_kv:
            with parent:
                pass
            assert deactivate.call_count == 1
            assert log_kv.call_count == 0

    parent.set_tag('x', 'y').set_tag('z', 1)  # test chaining
    parent.set_tag(tags.PEER_SERVICE, 'test-service')
    parent.set_tag(tags.PEER_HOST_IPV4, 127 << 24 + 1)
    parent.set_tag(tags.PEER_HOST_IPV6, '::')
    parent.set_tag(tags.PEER_HOSTNAME, 'uber.com')
    parent.set_tag(tags.PEER_PORT, 123)
    parent.deactivate()


def test_wrapped():
    tracer = Tracer()
    span = tracer.start_active_span()
    assert span.wrapped is not None

    span.set_operation_name('a')
    span.set_baggage_item('key1', 'value1')
    span.get_baggage_item('key1')
    span.log_kv({})
    span.log_event('event1')


def test_capture():
    tracer = Tracer()
    span = tracer.start_active_span()
    continuation = span.capture()
    assert continuation is not None
    assert continuation.activate() is not None
