from __future__ import print_function

import asyncio

from opentracing.mocktracer import MockTracer
from opentracing.scope_managers.contextvars import ContextVarsScopeManager
from ..testcase import OpenTracingTestCase
from ..utils import get_logger, stop_loop_when


logger = get_logger(__name__)


class TestAsyncioContextVars(OpenTracingTestCase):
    def setUp(self):
        self.tracer = MockTracer(ContextVarsScopeManager())
        self.loop = asyncio.get_event_loop()

    def test_main(self):

        parent_scope = self.tracer.start_active_span('parent')
        self.submit_subtasks()

        stop_loop_when(self.loop,
                       lambda: len(self.tracer.finished_spans()) >= 2)
        self.loop.run_forever()

        # Late-finish the parent Span now.
        parent_scope.close()

        spans = self.tracer.finished_spans()
        self.assertEqual(len(spans), 3)
        self.assertNamesEqual(spans, ['task1', 'task2', 'parent'])

        for i in range(2):
            self.assertSameTrace(spans[i], spans[-1])
            self.assertIsChildOf(spans[i], spans[-1])
            self.assertTrue(spans[i].finish_time <= spans[-1].finish_time)

    def submit_subtasks(self):
        async def task(name):
            logger.info('Running %s' % name)
            with self.tracer.start_active_span(name):
                await asyncio.sleep(0.1)

        self.loop.create_task(task('task1'))
        self.loop.create_task(task('task2'))
