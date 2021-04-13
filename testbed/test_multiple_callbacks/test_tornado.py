from __future__ import print_function

import random

from tornado import gen, ioloop

from opentracing.mocktracer import MockTracer
from opentracing.scope_managers.tornado import TornadoScopeManager, \
        tracer_stack_context
from ..testcase import OpenTracingTestCase
from ..utils import get_logger, stop_loop_when


random.seed()
logger = get_logger(__name__)


class TestTornado(OpenTracingTestCase):
    def setUp(self):
        self.tracer = MockTracer(TornadoScopeManager())
        self.loop = ioloop.IOLoop.current()

    def test_main(self):
        @gen.coroutine
        def main_task():
            with self.tracer.start_active_span('parent'):
                tasks = self.submit_callbacks()
                yield tasks

        with tracer_stack_context():
            self.loop.add_callback(main_task)

        stop_loop_when(self.loop,
                       lambda: len(self.tracer.finished_spans()) == 4)
        self.loop.start()

        spans = self.tracer.finished_spans()
        self.assertEquals(len(spans), 4)
        self.assertNamesEqual(spans, ['task', 'task', 'task', 'parent'])

        for i in range(3):
            self.assertSameTrace(spans[i], spans[-1])
            self.assertIsChildOf(spans[i], spans[-1])

    @gen.coroutine
    def task(self, interval, parent_span):
        logger.info('Starting task')

        # NOTE: No need to reactivate the parent_span, as TracerStackContext
        # keeps track of it, BUT a limitation is that, yielding
        # upon multiple coroutines, we cannot mess with the context,
        # so no active span set here.
        assert self.tracer.active_span is not None
        with self.tracer.start_span('task'):
            yield gen.sleep(interval)

    def submit_callbacks(self):
        parent_span = self.tracer.scope_manager.active.span
        tasks = []
        for i in range(3):
            interval = 0.1 + random.randint(200, 500) * 0.001
            t = self.task(interval, parent_span)
            tasks.append(t)

        return tasks

    def test_multiple_callbacks_scheduled_in_loop(self):
        """
        This test emulates concurrent execution of two scheduled callbacks.
        One callback has yield operation that switching context of execution to
        another one callback.
        When execution of first callback resumes back, it's active scope must
        be the same.
        """

        @gen.coroutine
        def callback_1(name):
            with self.tracer.start_active_span(name) as scope:
                yield gen.sleep(0.1)
                # Check that another concurrently executed callback doesn't
                # change original scope.
                self.assertEqual(self.tracer.scope_manager.active, scope)
                self.assertEqual(self.tracer.active_span, scope.span)

        def callback_2(name):
            with self.tracer.start_active_span(name):
                pass

        @gen.coroutine
        def main_task():
            with self.tracer.start_active_span('parent') as scope:
                # Each callback should be wrapped by their own stack context.
                with tracer_stack_context(scope.span):
                    self.loop.add_callback(callback_1, 'foo')
                with tracer_stack_context(scope.span):
                    self.loop.add_callback(callback_2, 'bar')

        with tracer_stack_context():
            self.loop.add_callback(main_task)

        stop_loop_when(self.loop,
                       lambda: len(self.tracer.finished_spans()) == 3)
        self.loop.start()

        parent, bar, foo = self.tracer.finished_spans()
        # Callbacks will be finished later than their parent.
        self.assertNamesEqual([parent, bar, foo], ['parent', 'bar', 'foo', ])

        self.assertSameTrace(parent, bar)
        self.assertSameTrace(parent, foo)

        self.assertIsChildOf(foo, parent)
        self.assertIsChildOf(bar, parent)

    def test_concurrent_fire_and_forget_coroutines(self):
        """
        This test emulates concurrent execution of fire & forget coroutines.
        Each coroutine has two yield operation that switching context of
        execution to another one coroutine.
        When execution of a coroutine resumes back, it's active scope must be
        the same.
        """

        @gen.coroutine
        def coro(name):
            with self.tracer.start_active_span(name) as scope:
                yield gen.sleep(0.1)
                # Check that another concurrently executed coroutine doesn't
                # change original scope.
                self.assertEqual(self.tracer.scope_manager.active, scope)
                self.assertEqual(self.tracer.active_span, scope.span)
                yield gen.sleep(0.1)

        @gen.coroutine
        def main_task():
            with self.tracer.start_active_span('parent') as scope:
                # Each coroutine should be wrapped by their own stack context.
                with tracer_stack_context(scope.span):
                    coro('foo')
                with tracer_stack_context(scope.span):
                    coro('bar')

        with tracer_stack_context():
            main_task()

        stop_loop_when(self.loop,
                       lambda: len(self.tracer.finished_spans()) == 3)
        self.loop.start()

        parent, foo, bar = self.tracer.finished_spans()
        # Coroutines will be finished later than their parent.
        self.assertNamesEqual([parent, foo, bar], ['parent', 'foo', 'bar', ])

        self.assertSameTrace(parent, foo)
        self.assertSameTrace(parent, bar)

        self.assertIsChildOf(foo, parent)
        self.assertIsChildOf(bar, parent)
