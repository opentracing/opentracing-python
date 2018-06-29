from __future__ import print_function

import asyncio

from opentracing.mocktracer import MockTracer
from opentracing.ext.scope_manager.asyncio import AsyncioScopeManager
from ..testcase import OpenTracingTestCase
from ..utils import get_logger, stop_loop_when


logger = get_logger(__name__)


class TestAsyncio(OpenTracingTestCase):
    def setUp(self):
        self.tracer = MockTracer(AsyncioScopeManager())
        self.loop = asyncio.get_event_loop()

    def test_main(self):
        # Create a Span and use it as (explicit) parent of a pair of subtasks.
        parent_span = self.tracer.start_span('parent')
        self.submit_subtasks(parent_span)

        stop_loop_when(self.loop,
                       lambda: len(self.tracer.finished_spans()) >= 2)
        self.loop.run_forever()

        # Late-finish the parent Span now.
        parent_span.finish()

        spans = self.tracer.finished_spans()
        self.assertEqual(len(spans), 3)
        self.assertNamesEqual(spans, ['task1', 'task2', 'parent'])

        for i in range(2):
            self.assertSameTrace(spans[i], spans[-1])
            self.assertIsChildOf(spans[i], spans[-1])
            self.assertTrue(spans[i].finish_time <= spans[-1].finish_time)

    # Fire away a few subtasks, passing a parent Span whose lifetime
    # is not tied at all to the children.
    def submit_subtasks(self, parent_span):
        async def task(name):
            logger.info('Running %s' % name)
            with self.tracer.scope_manager.activate(parent_span, False):
                with self.tracer.start_active_scope(name):
                    asyncio.sleep(0.1)

        self.loop.create_task(task('task1'))
        self.loop.create_task(task('task2'))
