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


class ActiveSpanSource(object):
    """ActiveSpanSource allows an existing execution context provider
    to act as a source for an actively-scheduled OpenTracing Span.
    """
    def __init__(self):
        self._noop_active_span = None

    @property
    def active_span(self):
        """Return the current active span.

        If there is an ActiveSpanSource.active_span, it becomes an implicit
        parent of any newly-created span at Tracer.start_active_span() time.

        :return: Returns the active Span, or None, if none could be found.
        """
        return self._noop_active_span

    def make_active(self, span):
        """Make a given the span active for the current execution
        context.

        :param span: The Span to make active.

        :return: Returns the Span itself, for call chaining.
        """
        return self._noop_active_span

    def deactivate(self, span):
        """Mark the end of the active period for the current context and
        Span. If the passed Span is not ActiveSpanSource.active_span,
        nothing is done.
        """
        pass
