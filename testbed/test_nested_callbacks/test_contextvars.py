from __future__ import print_function


import asyncio

from opentracing.mocktracer import MockTracer
from opentracing.scope_managers.contextvars import ContextVarsScopeManager, \
    no_parent_scope
from ..testcase import OpenTracingTestCase
from ..utils import stop_loop_when


class TestAsyncioContextVars(OpenTracingTestCase):

    def setUp(self):
        self.tracer = MockTracer(ContextVarsScopeManager())
        self.loop = asyncio.get_event_loop()

    def test_main(self):

        def submit():
            span = self.tracer.scope_manager.active.span

            async def task1():
                self.assertEqual(span, self.tracer.active_span)
                self.tracer.active_span.set_tag('key1', '1')

                async def task2():
                    self.assertEqual(span, self.tracer.active_span)
                    self.tracer.active_span.set_tag('key2', '2')

                    async def task3():
                        self.assertEqual(span, self.tracer.active_span)
                        self.tracer.active_span.set_tag('key3', '3')
                        self.tracer.active_span.finish()

                    self.loop.create_task(task3())

                self.loop.create_task(task2())

            self.loop.create_task(task1())

        # Start a Span and let the callback-chain
        # finish it when the task is done
        async def task():
            with self.tracer.start_active_span('one', finish_on_close=False):
                submit()

        self.loop.create_task(task())

        stop_loop_when(self.loop,
                       lambda: len(self.tracer.finished_spans()) == 1)
        self.loop.run_forever()

        span, = self.tracer.finished_spans()
        self.assertEqual(span.operation_name, 'one')

        for i in range(1, 4):
            self.assertEqual(span.tags.get('key%s' % i, None), str(i))


class TestAsyncioContextVarsScheduleInLoop(OpenTracingTestCase):

    # TODO: move the test-case to another file

    def setUp(self):
        self.tracer = MockTracer(ContextVarsScopeManager())
        self.loop = asyncio.get_event_loop()

    def test_schedule_callbacks(self):

        def callback(op_name):
            with self.tracer.start_active_span(
                operation_name=op_name,
                child_of=self.tracer.active_span,
            ):
                pass

        def callback_with_nested_callback(op_name):
            with self.tracer.start_active_span(
                operation_name=op_name,
                child_of=self.tracer.active_span,
            ):
                self.loop.call_soon(callback, 'childof:{}'.format(op_name))

        with self.tracer.start_active_span('root'):
            self.loop.call_soon(callback_with_nested_callback, 'first')
            self.loop.call_soon(callback, 'second')

        stop_loop_when(self.loop,
                       lambda: len(self.tracer.finished_spans()) == 4)
        self.loop.run_forever()

        root, first, second, childof_first = self.tracer.finished_spans()
        self.assertEmptySpan(root, 'root')
        self.assertEmptySpan(first, 'first')
        self.assertEmptySpan(second, 'second')
        self.assertEmptySpan(childof_first, 'childof:first')

        self.assertIsChildOf(first, root)
        self.assertIsChildOf(childof_first, first)
        self.assertIsChildOf(second, root)

    def test_coroutines_schedule_callbacks(self):

        def callback(op_name):
            with self.tracer.start_active_span(
                operation_name=op_name,
                child_of=self.tracer.active_span
            ):
                pass

        async def task(op_name):
            with self.tracer.start_active_span(
                operation_name=op_name,
                child_of=self.tracer.active_span
            ):
                self.loop.call_later(
                    0.1, callback, 'childof:{}'.format(op_name)
                )
        with self.tracer.start_active_span('root'):
            self.loop.create_task(task('task1'))
            self.loop.create_task(task('task2'))

        stop_loop_when(self.loop,
                       lambda: len(self.tracer.finished_spans()) == 5)
        self.loop.run_forever()

        root, task1, task2, child1, child2 = self.tracer.finished_spans()

        self.assertEmptySpan(root, 'root')
        self.assertEmptySpan(task1, 'task1')
        self.assertEmptySpan(task2, 'task2')
        self.assertEmptySpan(child1, 'childof:task1')
        self.assertEmptySpan(child2, 'childof:task2')

        self.assertIsChildOf(task1, root)
        self.assertIsChildOf(task2, root)
        self.assertIsChildOf(child1, task1)
        self.assertIsChildOf(child2, task2)

    def test_coroutines_scheduling_task(self):

        async def _task(op_name):
            await asyncio.sleep(0.1)
            with self.tracer.start_active_span(
                operation_name=op_name,
                child_of=self.tracer.active_span
            ):
                pass

        async def task(op_name):
            with self.tracer.start_active_span(
                operation_name=op_name,
                child_of=self.tracer.active_span
            ):
                self.loop.create_task(_task('childof:{}'.format(op_name)))

        with self.tracer.start_active_span('root'):
            self.loop.create_task(task('task1'))
            self.loop.create_task(task('task2'))

        stop_loop_when(self.loop,
                       lambda: len(self.tracer.finished_spans()) == 5)
        self.loop.run_forever()

        root, task1, task2, child1, child2 = self.tracer.finished_spans()

        self.assertEmptySpan(root, 'root')
        self.assertEmptySpan(task1, 'task1')
        self.assertEmptySpan(task2, 'task2')
        self.assertEmptySpan(child1, 'childof:task1')
        self.assertEmptySpan(child2, 'childof:task2')

        self.assertIsChildOf(task1, root)
        self.assertIsChildOf(task2, root)
        self.assertIsChildOf(child1, task1)
        self.assertIsChildOf(child2, task2)

    def test_recursive_scheduling_task(self):

        tasks = 4

        async def task(n=0):
            await asyncio.sleep(0.1)
            with self.tracer.start_active_span(
                operation_name=str(n),
                child_of=self.tracer.active_span
            ):
                if n < tasks:
                    self.loop.create_task(task(n+1))

        self.loop.create_task(task())

        stop_loop_when(self.loop,
                       lambda: len(self.tracer.finished_spans()) == tasks)
        self.loop.run_forever()

        spans = self.tracer.finished_spans()

        for i in range(tasks):
            self.assertEmptySpan(spans[i], str(i))
            if i == 0:
                self.assertIsNone(spans[i].parent_id)
            else:
                self.assertIsChildOf(spans[i], spans[i-1])

    def test_recursive_scheduling_with_ignoring_active_span(self):

        tasks = 4

        async def task(n=0):
            await asyncio.sleep(0.1)
            if n < tasks / 2:
                with self.tracer.start_active_span(str(n)):
                    self.loop.create_task(task(n+1))
            elif n < tasks:
                with self.tracer.start_active_span(
                    operation_name=str(n),
                    ignore_active_span=True
                ):
                    self.loop.create_task(task(n+1))

        self.loop.create_task(task())

        stop_loop_when(self.loop,
                       lambda: len(self.tracer.finished_spans()) == tasks)
        self.loop.run_forever()

        s0, s1, s2, s3 = self.tracer.finished_spans()

        self.assertEmptySpan(s0, '0')
        self.assertHasNoParent(s0)

        self.assertEmptySpan(s1, '1')
        self.assertIsChildOf(s1, s0)

        self.assertEmptySpan(s2, '2')
        self.assertHasNoParent(s2)

        self.assertEmptySpan(s3, '3')
        self.assertHasNoParent(s3)

    def test_tasks_with_no_parent_scope(self):

        async def task(name):
            await asyncio.sleep(0.1)
            with self.tracer.start_active_span(name):
                await asyncio.sleep(0.1)

        async def tasks():
            self.loop.create_task(task('task_1'))
            with no_parent_scope():
                self.loop.create_task(task('task_2'))
            self.loop.create_task(task('task_3'))

        with self.tracer.start_active_span('root'):
            self.loop.create_task(tasks())

        stop_loop_when(self.loop,
                       lambda: len(self.tracer.finished_spans()) == 4)
        self.loop.run_forever()

        root, task1, task2, task3 = self.tracer.finished_spans()

        self.assertEmptySpan(root, 'root')

        self.assertEmptySpan(task1, 'task_1')
        self.assertIsChildOf(task1, root)

        # Third task was scheduled out `no_parent_scope`.
        self.assertEmptySpan(task3, 'task_3')
        self.assertIsChildOf(task3, root)

        # Second task "wrapped" by `no_parent_scope`.
        self.assertEmptySpan(task2, 'task_2')
        self.assertHasNoParent(task2)

    def test_callbacks_with_no_parent_scope(self):

        def callback(name):
            with self.tracer.start_active_span(name):
                pass

        def callbacks():
            self.loop.call_soon(callback, 'task_1')
            with no_parent_scope():
                self.loop.call_soon(callback, 'task_2')
            self.loop.call_soon(callback, 'task_3')

        with self.tracer.start_active_span('root'):
            self.loop.call_soon(callbacks)

        stop_loop_when(self.loop,
                       lambda: len(self.tracer.finished_spans()) == 4)
        self.loop.run_forever()

        root, task1, task2, task3 = self.tracer.finished_spans()

        self.assertEmptySpan(root, 'root')

        self.assertEmptySpan(task1, 'task_1')
        self.assertIsChildOf(task1, root)

        # Third task was scheduled out `no_parent_scope`.
        self.assertEmptySpan(task3, 'task_3')
        self.assertIsChildOf(task3, root)

        # Second task "wrapped" by `no_parent_scope`.
        self.assertEmptySpan(task2, 'task_2')
        self.assertHasNoParent(task2)

    def test_await_with_no_parent_scope(self):

        async def coro(name):
            with self.tracer.start_active_span(name):
                pass

        async def main_coro():
            await coro('coro_1')
            with no_parent_scope():
                await coro('coro_2')
            await coro('coro_3')

        with self.tracer.start_active_span('root'):
            self.loop.create_task(main_coro())

        stop_loop_when(self.loop,
                       lambda: len(self.tracer.finished_spans()) == 4)
        self.loop.run_forever()

        root, coro1, coro2, coro3 = self.tracer.finished_spans()

        self.assertEmptySpan(root, 'root')

        self.assertEmptySpan(coro1, 'coro_1')
        self.assertIsChildOf(coro1, root)

        # second coroutine "wrapped" by `no_parent_scope`.
        self.assertEmptySpan(coro2, 'coro_2')
        self.assertHasNoParent(coro2)

        self.assertEmptySpan(coro3, 'coro_3')
        self.assertIsChildOf(coro3, root)
