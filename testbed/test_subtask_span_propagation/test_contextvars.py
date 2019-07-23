from __future__ import absolute_import, print_function

import asyncio

from opentracing.mocktracer import MockTracer
from opentracing.scope_managers.asyncio import AsyncioScopeManager
from ..testcase import OpenTracingTestCase


class TestAsyncioContextVars(OpenTracingTestCase):
    def setUp(self):
        self.tracer = MockTracer(AsyncioScopeManager())
        self.loop = asyncio.get_event_loop()

    def test_main(self):
        res = self.loop.run_until_complete(self.parent_task('message'))
        self.assertEqual(res, 'message::response')

        child, parent = self.tracer.finished_spans()
        self.assertEmptySpan(child, 'child')
        self.assertEmptySpan(parent, 'parent')
        self.assertIsChildOf(child, parent)

    async def parent_task(self, message):
        with self.tracer.start_active_span('parent'):
            res = await self.child_task(message)

        return res

    async def child_task(self, message):
        with self.tracer.start_active_span('child'):
            return '%s::response' % message
