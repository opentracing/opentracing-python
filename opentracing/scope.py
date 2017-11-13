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
    """
    A `Scope` formalizes the activation and deactivation of a `Span`, usually
    from a CPU standpoint. Many times a `Span` will be extant (in that
    `Span#finish()` has not been called) despite being in a non-runnable state
    from a CPU/scheduler standpoint. For instance, a `Span` representing the
    client side of an RPC will be unfinished but blocked on IO while the RPC is
    still outstanding. A `Scope` defines when a given `Span` is scheduled
    and on the path.
    """
    def __init__(self, span):
        """
        Initialize a `Scope` for the given `Span` object

        :param span: the `Span` used for this `Scope`
        """
        # TODO: maybe it should always be the NoopSpan?
        # something similar to:
        # self._noop_span_context = SpanContext()
        # self._noop_span = Span(tracer=self, context=self._noop_span_context)
        self._span = span

    def span(self):
        """
        Return the `Span` that's been scoped by this `Scope`.
        """
        return self._span

    def close(self):
        """
        Mark the end of the active period for the current thread and `Scope`,
        updating the `ScopeManager#active()` in the process.

        NOTE: Calling `close()` more than once on a single `Scope` instance
        leads to undefined behavior.
        """
        pass

    def __enter__(self):
        """
        Allow `Scope` to be used inside a Python Context Manager.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Call `close()` when the execution is outside the Python
        Context Manager.
        """
        self.close()
