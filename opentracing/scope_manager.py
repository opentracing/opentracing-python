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

from .span import Span, SpanContext
from .scope import Scope


class ScopeManager(object):
    """The :class:`ScopeManager` interface abstracts both the activation of
    a span and access to an active span/scope.
    """
    def __init__(self):
        # TODO: `tracer` should not be None, but we don't have a reference;
        # should we move the NOOP SpanContext, Span, Scope to somewhere
        # else so that they're globally reachable?
        self._noop_span = Span(tracer=None, context=SpanContext())
        self._noop_scope = Scope(self, self._noop_span)

    def activate(self, span, finish_on_close):
        """Makes a span active.

        :param span: the span that should become active.
        :param finish_on_close: whether span should be automatically
            finished when :meth:`Scope.close()` is called.

        :rtype: Scope
        :return: a scope to control the end of the active period for *span*. It
            is a programming error to neglect to call :meth:`Scope.close()` on
            the returned instance.
        """
        return self._noop_scope

    @property
    def active(self):
        """Returns the currently active scope which can be used to access the
        currently active :attr:`Scope.span`.

        If there is a non-null scope, its wrapped span becomes an implicit
        parent of any newly-created span at :meth:`Tracer.start_active_span()`
        time.

        :rtype: Scope
        :return: the scope that is active, or ``None`` if not available.
        """
        return self._noop_scope
