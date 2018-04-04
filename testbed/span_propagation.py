import six
import threading
from tornado.stack_context import StackContext
import gevent.local

from opentracing import ScopeManager, Scope

if six.PY3:
    import asyncio


#
# asyncio section.
#
class AsyncioScopeManager(ScopeManager):
    def activate(self, span, finish_on_close):
        scope = AsyncioScope(self, span, finish_on_close)

        loop = asyncio.get_event_loop()
        task = asyncio.Task.current_task(loop=loop)
        setattr(task, '__active', scope)

        return scope

    def _get_current_task(self):
        loop = asyncio.get_event_loop()
        return asyncio.Task.current_task(loop=loop)

    @property
    def active(self):
        task = self._get_current_task()
        return getattr(task, '__active', None)


class AsyncioScope(Scope):
    def __init__(self, manager, span, finish_on_close):
        super(AsyncioScope, self).__init__(manager, span)
        self._finish_on_close = finish_on_close
        self._to_restore = manager.active

    def close(self):
        if self.manager.active is not self:
            return

        task = self.manager._get_current_task()
        setattr(task, '__active', self._to_restore)

        if self._finish_on_close:
            self.span.finish()

#
# gevent section.
#
class GeventScopeManager(ScopeManager):
    def __init__(self):
        self._locals = gevent.local.local()

    def activate(self, span, finish_on_close):
        scope = GeventScope(self, span, finish_on_close)
        setattr(self._locals, 'active', scope)

        return scope

    @property
    def active(self):
        return getattr(self._locals, 'active', None)


class GeventScope(Scope):
    def __init__(self, manager, span, finish_on_close):
        super(GeventScope, self).__init__(manager, span)
        self._finish_on_close = finish_on_close
        self._to_restore = manager.active

    def close(self):
        if self.manager.active is not self:
            return

        setattr(self.manager._locals, 'active', self._to_restore)

        if self._finish_on_close:
            self.span.finish()

#
# tornado section.
#
class TornadoScopeManager(ScopeManager):
    def activate(self, span, finish_on_close):
        context = self._get_context()
        if context is None:
            raise Exception('No StackContext detected')

        scope = TornadoScope(self, span, finish_on_close)
        context.active = scope

        return scope

    def _get_context(self):
        return TracerRequestContextManager.current_context()

    @property
    def active(self):
        context = self._get_context()
        if context is None:
            return None

        return context.active


class TornadoScope(Scope):
    def __init__(self, manager, span, finish_on_close):
        super(TornadoScope, self).__init__(manager, span)
        self._finish_on_close = finish_on_close
        self._to_restore = manager.active

    def close(self):
        context = self.manager._get_context()
        if context is None or context.active is not self:
            return

        context.active = self._to_restore

        if self._finish_on_close:
            self.span.finish()


class TracerRequestContext(object):
    __slots__ = ('active', )

    def __init__(self, active=None):
        self.active = active


class TracerRequestContextManager(object):
    _state = threading.local()
    _state.context = None

    @classmethod
    def current_context(cls):
        return getattr(cls._state, 'context', None)

    def __init__(self, context):
        self._context = context

    def __enter__(self):
        self._prev_context = self.__class__.current_context()
        self.__class__._state.context = self._context
        return self._context

    def __exit__(self, *_):
        self.__class__._state.context = self._prev_context
        self._prev_context = None
        return False


def tracer_stack_context():
    context = TracerRequestContext()
    return StackContext(lambda: TracerRequestContextManager(context))
