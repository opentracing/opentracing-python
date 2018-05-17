# Copyright (c) The OpenTracing Authors.
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

import threading

from opentracing import Scope, ScopeManager


class ThreadLocalScopeManager(ScopeManager):
    """ScopeManager implementation that stores the current active `Scope`
    using thread-local storage.
    """
    def __init__(self):
        self._tls_scope = threading.local()

    def activate(self, span, finish_on_close):
        """Make a `Span` instance active.

        :param span: the `Span` that should become active.
        :param finish_on_close: whether span should automatically be
            finished when `Scope#close()` is called.

        :return: a `Scope` instance to control the end of the active period for
            the `Span`. It is a programming error to neglect to call
            `Scope#close()` on the returned instance.
        """
        scope = ThreadLocalScope(self, span, finish_on_close)
        setattr(self._tls_scope, 'active', scope)
        return scope

    @property
    def active(self):
        """Return the currently active `Scope` which can be used to access the
        currently active `Scope#span`.

        If there is a non-null `Scope`, its wrapped `Span` becomes an implicit
        parent of any newly-created `Span` at `Tracer#start_span()`/
        `Tracer#start_active_span()` time.

        :return: the `Scope` that is active, or `None` if not available.
        """
        return getattr(self._tls_scope, 'active', None)


class ThreadLocalScope(Scope):
    """ThreadLocalScope is an implementation of `opentracing.Scope`
    using thread-local storage."""

    def __init__(self, manager, span, finish_on_close):
        """Initialize a `Scope` for the given `Span` object.

        :param span: the `Span` wrapped by this `Scope`.
        :param finish_on_close: whether span should automatically be
            finished when `Scope#close()` is called.
        """
        super(ThreadLocalScope, self).__init__(manager, span)
        self._finish_on_close = finish_on_close
        self._to_restore = manager.active

    def close(self):
        """Mark the end of the active period for this {@link Scope},
        updating ScopeManager#active in the process.
        """
        if self.manager.active is not self:
            return

        if self._finish_on_close:
            self.span.finish()

        setattr(self._manager._tls_scope, 'active', self._to_restore)
