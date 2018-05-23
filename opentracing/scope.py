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


class Scope(object):
    """A scope formalizes the activation and deactivation of a span, usually
    from a CPU standpoint. Many times a span will be extant (in that
    :meth:`Span.finish()` has not been called) despite being in a non-runnable
    state from a CPU/scheduler standpoint. For instance, a span representing
    the client side of an RPC will be unfinished but blocked on IO while the
    RPC is still outstanding. A scope defines when a given span is scheduled
    and on the path.

    :param manager: the scope manager that created this scope.
    :type manager: ScopeManager

    :param span: the span used for this scope.
    :type span: Span
    """
    def __init__(self, manager, span):
        """Initializes a scope for *span*."""
        self._manager = manager
        self._span = span

    @property
    def span(self):
        """Returns the span wrapped by this scope.

        :rtype: Span
        """
        return self._span

    @property
    def manager(self):
        """Returns the scope manager that created this scope.

        :rtype: ScopeManager
        """
        return self._manager

    def close(self):
        """Marks the end of the active period for this scope, updating
        :attr:`ScopeManager.active` in the process.

        NOTE: Calling this method more than once on a single scope leads to
        undefined behavior.
        """
        pass

    def __enter__(self):
        """Allows `Scope` to be used inside a Python Context Manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Calls :meth:`close()` when the execution is outside the Python
        Context Manager.
        """
        self.close()
