from __future__ import absolute_import, print_function

import functools

from tornado import gen, ioloop

from opentracing.mocktracer import MockTracer
from opentracing.scope_managers.tornado import TornadoScopeManager, \
        tracer_stack_context
from ..testcase import OpenTracingTestCase
from ..utils import stop_loop_when


class TestTornado(OpenTracingTestCase):
    def setUp(self):
        self.tracer = MockTracer(TornadoScopeManager())
        self.loop = ioloop.IOLoop.current()

    def test_main(self):

        @gen.coroutine
        def child_task(message):
            # No need to pass/activate the parent Span, as
            # it stays in the context.
            with self.tracer.start_active_span('child'):
                raise gen.Return('%s::response' % message)

        @gen.coroutine
        def parent_task(message):
            with self.tracer.start_active_span('parent'):
                res = yield child_task(message)

            raise gen.Return(res)

        parent_task = functools.partial(parent_task, 'message')
        with tracer_stack_context():
            res = self.loop.run_sync(parent_task)
        self.assertEqual(res, 'message::response')

        spans = self.tracer.finished_spans()
        self.assertEqual(len(spans), 2)
        self.assertNamesEqual(spans, ['child', 'parent'])
        self.assertIsChildOf(spans[0], spans[1])

    def test_callbacks(self):

        def child_callback_2():
            with self.tracer.start_active_span('child_2'):
                pass

        def child_callback_1():
            with self.tracer.start_active_span('child_1') as scope:
                # Should be wrapped by `tracer_stack_context` to store right
                # context in scheduled callback.
                with tracer_stack_context(scope.span):
                    self.loop.add_callback(child_callback_2)

        def parent_callback():
            with self.tracer.start_active_span('parent') as scope:
                with tracer_stack_context(scope.span):
                    self.loop.add_callback(child_callback_1)

        with tracer_stack_context():
            self.loop.add_callback(parent_callback)

        stop_loop_when(self.loop,
                       lambda: len(self.tracer.finished_spans()) == 3)
        self.loop.start()

        # Callback will be finished later than their parent.
        parent, child_1, child_2 = self.tracer.finished_spans()
        self.assertNamesEqual(
            [parent, child_1, child_2], ['parent', 'child_1', 'child_2'])
        self.assertSameTrace(child_1, parent)
        self.assertSameTrace(child_2, parent)

        self.assertIsChildOf(child_1, parent)
        self.assertIsChildOf(child_2, child_1)

    def test_fire_and_forget_coroutines(self):

        @gen.coroutine
        def child_coro_2():
            yield gen.sleep(0.1)
            with self.tracer.start_active_span('child_2'):
                pass

        @gen.coroutine
        def child_coro_1():
            with self.tracer.start_active_span('child_1') as scope:
                # Should be wrapped by `tracer_stack_context` to store right
                # context in scheduled callback.
                yield gen.sleep(0.1)
                with tracer_stack_context(scope.span):
                    child_coro_2()

        @gen.coroutine
        def parent_coro():
            with self.tracer.start_active_span('parent') as scope:
                with tracer_stack_context(scope.span):
                    child_coro_1()

        with tracer_stack_context():
            parent_coro()

        stop_loop_when(self.loop,
                       lambda: len(self.tracer.finished_spans()) == 3)
        self.loop.start()

        # Callback will be finished later than their parent.
        parent, child_1, child_2 = self.tracer.finished_spans()
        self.assertNamesEqual(
            [parent, child_1, child_2], ['parent', 'child_1', 'child_2'])
        self.assertSameTrace(child_1, parent)
        self.assertSameTrace(child_2, parent)

        self.assertIsChildOf(child_1, parent)
        self.assertIsChildOf(child_2, child_1)
