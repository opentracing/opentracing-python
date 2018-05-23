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

import asyncio

from opentracing import Scope, ScopeManager


class AsyncioScopeManager(ScopeManager):
    """
    :class:`~opentracing.ScopeManager` implementation for **asyncio**
    that stores the :class:`~opentracing.Scope` in the current
    :class:`Task` (:meth:`Task.current_task()`).

    It needs both an existing loop for the current thread
    (:meth:`asyncio.get_event_loop()`) and to be accesed under a running
    coroutine. Automatic :class:`~opentracing.Span` propagation from
    parent coroutines to their children is not provided, which needs to be
    done manually:

    .. code-block:: python

        async def child_coroutine(span):
            # activate the parent Span, but do not finish it upon
            # deactivation. That will be done by the parent coroutine.
            with tracer.scope_manager.activate(span, finish_on_close=False):
                with tracer.start_active_span('child') as scope:
                    ...

        async def parent_coroutine():
            with tracer.start_active_span('parent') as scope:
                ...
                await child_coroutine(span)
                ...

    """

    def activate(self, span, finish_on_close):
        """
        Make a :class:`~opentracing.Span` instance active.

        :param span: the :class:`~opentracing.Span` that should become active.
        :param finish_on_close: whether *span* should automatically be
            finished when :meth:`Scope.close()` is called.

        RuntimeError will be raised if no :class:`Task` is being
        executed (:meth:`Task.current_task()` returning ``None``).

        :return: a :class:`~opentracing.Scope` instance to control the end
            of the active period for the :class:`~opentracing.Span`.
            It is a programming error to neglect to call :meth:`Scope.close()`
            on the returned instance.
        """

        scope = _AsyncioScope(self, span, finish_on_close)
        self._set_active(scope)

        return scope

    @property
    def active(self):
        """
        Return the currently active :class:`~opentracing.Scope` which
        can be used to access the currently active
        :attr:`Scope.span`.

        If no :class:`Task` is being executed, this property will
        return ``None``.

        :return: the :class:`~opentracing.Scope` that is active,
            or ``None`` if not available.
        """

        loop = asyncio.get_event_loop()
        task = asyncio.Task.current_task(loop=loop)
        return getattr(task, '__active', None)

    def _set_active(self, scope):
        loop = asyncio.get_event_loop()
        task = asyncio.Task.current_task(loop=loop)
        if not task:
            raise RuntimeError('No executing Task detected.')

        setattr(task, '__active', scope)


class _AsyncioScope(Scope):
    def __init__(self, manager, span, finish_on_close):
        super(_AsyncioScope, self).__init__(manager, span)
        self._finish_on_close = finish_on_close
        self._to_restore = manager.active

    def close(self):
        if self.manager.active is not self:
            return

        self._manager._set_active(self._to_restore)

        if self._finish_on_close:
            self.span.finish()
