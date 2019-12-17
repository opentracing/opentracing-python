from __future__ import absolute_import, print_function

import asyncio

from opentracing.mocktracer import MockTracer
from opentracing.scope_managers.asyncio import AsyncioScopeManager
from ..testcase import OpenTracingTestCase


class TestAsyncio(OpenTracingTestCase):
    def setUp(self):
        self.tracer = MockTracer(AsyncioScopeManager())
        self.loop = asyncio.get_event_loop()

    def test_main(self):
        res = self.loop.run_until_complete(self.parent_task('message'))
        self.assertEqual(res, 'message::response')

        spans = self.tracer.finished_spans()
        self.assertEqual(len(spans), 2)
        self.assertNamesEqual(spans, ['child', 'parent'])
        self.assertIsChildOf(spans[0], spans[1])

    async def parent_task(self, message):  # noqa
        with self.tracer.start_active_span('parent') as scope:
            res = await self.child_task(message, scope.span)

        return res

    async def child_task(self, message, span):
        with self.tracer.scope_manager.activate(span, False):
            with self.tracer.start_active_span('child'):
                return '%s::response' % message
