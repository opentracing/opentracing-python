# Copyright (c) 2017 The OpenTracing Authors.
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

from threading import Lock, local
from ..span import ActiveSpan
from ..span import ActiveSpanContinuation
from ..tracer import ActiveSpanSource


class ThreadLocalActiveSpanSource(ActiveSpanSource):
    """
    A simple ActiveSpanSource implementation built on top of
    Python's thread-local storage.
    """

    def __init__(self):
        self._tls_snapshot = local()

    @property
    def active_span(self):
        return getattr(self._tls_snapshot, 'active_span', None)

    def _set_active_span(self, active_span):
        self._tls_snapshot.active_span = active_span

    def make_active(self, span):
        return ThreadLocalActiveSpan(self, span, _RefCount(1))


class _RefCount(object):
    def __init__(self, initial_value):
        self._value = initial_value
        self._lock = Lock()

    def increment_and_get(self):
        with self._lock:
            self._value += 1
            return self._value

    def decrement_and_get(self):
        with self._lock:
            self._value -= 1
            return self._value


class ThreadLocalActiveSpan(ActiveSpan):
    """
    A simple ActiveSpan implementation that relies on
    Python's thread-local storage.
    """
    def __init__(self, source, wrapped, refcount):
        super(ThreadLocalActiveSpan, self).__init__(wrapped)
        self._source = source
        self._refcount = refcount

        self._to_restore = source.active_span
        source._set_active_span(self)

    def deactivate(self):
        if self._source.active_span is not self:
            # This shouldn't happen if users call methods in the expected
            # order. Bail out.
            return

        self._source._set_active_span(self._to_restore)

        if self._refcount.decrement_and_get() == 0:
            self.wrapped.finish()

    def capture(self):
        return ThreadLocalActiveSpanContinuation(self)


class ThreadLocalActiveSpanContinuation(ActiveSpanContinuation):
    def __init__(self, active_span):
        super(ThreadLocalActiveSpanContinuation, self).__init__()
        self._active_span = active_span
        self._active_span._refcount.increment_and_get()

    def activate(self):
        return ThreadLocalActiveSpan(
            self._active_span._source,
            self._active_span.wrapped,
            self._active_span._refcount
        )
