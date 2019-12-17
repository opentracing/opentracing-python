from __future__ import print_function

import asyncio

from opentracing.mocktracer import MockTracer
from ..testcase import OpenTracingTestCase
from opentracing.scope_managers.contextvars import ContextVarsScopeManager
from ..utils import stop_loop_when


class TestAsyncioContextVars(OpenTracingTestCase):
    def setUp(self):
        self.tracer = MockTracer(ContextVarsScopeManager())
        self.loop = asyncio.get_event_loop()

    def test_main(self):
        # Start an isolated task and query for its result -and finish it-
        # in another task/thread
        span = self.tracer.start_span('initial')
        self.submit_another_task(span)

        stop_loop_when(self.loop,
                       lambda: len(self.tracer.finished_spans()) >= 3)
        self.loop.run_forever()

        initial, subtask, task = self.tracer.finished_spans()

        self.assertEmptySpan(initial, 'initial')
        self.assertEmptySpan(subtask, 'subtask')
        self.assertEmptySpan(task, 'task')

        # task/subtask are part of the same trace,
        # and subtask is a child of task
        self.assertSameTrace(subtask, task)
        self.assertIsChildOf(subtask, task)

        # initial task is not related in any way to those two tasks
        self.assertNotSameTrace(initial, subtask)
        self.assertHasNoParent(initial)

    async def task(self, span):
        # Create a new Span for this task
        with self.tracer.start_active_span('task'):

            with self.tracer.scope_manager.activate(span, True):
                # Simulate work strictly related to the initial Span
                pass

            # Use the task span as parent of a new subtask
            with self.tracer.start_active_span('subtask'):
                pass

    def submit_another_task(self, span):
        self.loop.create_task(self.task(span))
