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

import gevent.local

from opentracing import Scope, ScopeManager


class GeventScopeManager(ScopeManager):
    """ScopeManager implementation for gevent that stores
    the `Scope` in greenlet-local storage (gevent.local.local).

    Automatic `Span` propagation from parent greenlets to
    their children is not provided, which needs to be
    done manually:

    .. code-block:: python

        def child_greenlet(span):
            # activate the parent Span, but do not finish it upon
            # deactivation. That will be done by the parent greenlet.
            with tracer.scope_manager.activate(span, finish_on_close=False):
                with tracer.start_active_span('child') as scope:
                    ...

        def parent_greenlet():
            with tracer.start_active_span('parent') as scope:
                ...
                gevent.spawn(child_greenlet, span).join()
                ...

    """
    def __init__(self):
        self._locals = gevent.local.local()

    def activate(self, span, finish_on_close):
        scope = _GeventScope(self, span, finish_on_close)
        setattr(self._locals, 'active', scope)

        return scope

    @property
    def active(self):
        return getattr(self._locals, 'active', None)


class _GeventScope(Scope):
    def __init__(self, manager, span, finish_on_close):
        super(_GeventScope, self).__init__(manager, span)
        self._finish_on_close = finish_on_close
        self._to_restore = manager.active

    def close(self):
        if self.manager.active is not self:
            return

        setattr(self.manager._locals, 'active', self._to_restore)

        if self._finish_on_close:
            self.span.finish()
