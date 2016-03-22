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
from opentracing import Format
from opentracing import Tracer
from opentracing.ext import tags


def test_span():
    tracer = Tracer()
    parent = tracer.start_span('parent')
    child = tracer.start_span('test', parent=parent)
    assert parent == child
    child.log_event('cache_hit', ['arg1', 'arg2'])

    with mock.patch.object(parent, 'finish') as finish:
        with mock.patch.object(parent, 'log_event') as log_event:
            try:
                with parent:
                    raise ValueError()
            except ValueError:
                pass
            assert finish.call_count == 1
            assert log_event.call_count == 1

    with mock.patch.object(parent, 'finish') as finish:
        with mock.patch.object(parent, 'log_event') as log_event:
            with parent:
                pass
            assert finish.call_count == 1
            assert log_event.call_count == 0

    parent.set_tag('x', 'y').set_tag('z', 1)  # test chaining
    parent.set_tag(tags.PEER_SERVICE, 'test-service')
    parent.set_tag(tags.PEER_HOST_IPV4, 127 << 24 + 1)
    parent.set_tag(tags.PEER_HOST_IPV6, '::')
    parent.set_tag(tags.PEER_HOSTNAME, 'uber.com')
    parent.set_tag(tags.PEER_PORT, 123)
    parent.finish()


def test_inject():
    tracer = Tracer()
    span = tracer.start_span()

    bin_carrier = bytearray()
    tracer.inject(span=span, format=Format.BINARY, carrier=bin_carrier)
    assert bin_carrier == bytearray()

    text_carrier = {}
    tracer.inject(span=span, format=Format.TEXT_MAP, carrier=text_carrier)
    assert text_carrier == {}


def test_join():
    tracer = Tracer()
    noop_span = tracer._noop_span

    bin_carrier = bytearray()
    span = tracer.join('op_name', Format.BINARY, carrier=bin_carrier)
    assert noop_span == span

    text_carrier = {}
    span = tracer.join('op_name', Format.TEXT_MAP, carrier=text_carrier)
    assert noop_span == span
