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
from .span import Span
from .span import SpanContext


class BaseActiveSpanSource(object):
    """BaseActiveSpanSource is the interface for a pluggable class that
    keeps track of the current active `Span`. It must be used as a
    base class in specific implementations.
    """
    def make_active(self, span):
        """Sets the given `Span` as active, so that it is used as a parent
        when creating new spans. The implementation must keep track of the
        active spans sequence, so that previous spans can be resumed
        after a deactivation.

        :param span: the `Span` that is marked as active.
        """
        raise NotImplementedError

    @property
    def active_span(self):
        """Returns the `Span` that is currently activated for this source.

        :return: the current active `Span`
        """
        raise NotImplementedError

    def deactivate(self, span):
        """Deactivate the given `Span`, restoring the previous active one.
        This method must take in consideration that a `Span` may be deactivated
        when it's not really active. In that case, the current active stack
        must not be changed.

        :param span: the `Span` that must be deactivated
        """
        raise NotImplementedError


class NoopActiveSpanSource(BaseActiveSpanSource):
    """NoopActiveSpanSource provides the logic to get and set the current
    active `Span`. This is a cheap noop implementation that is used when
    a specific `Tracer` implementation is not used.
    """
    def __init__(self):
        self._noop_span_context = SpanContext()
        self._noop_span = Span(None, context=self._noop_span_context)

    def make_active(self, span):
        pass

    @property
    def active_span(self):
        return self._noop_span

    def deactivate(self, span):
        pass
