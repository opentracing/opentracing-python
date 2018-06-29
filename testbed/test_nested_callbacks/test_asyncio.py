from __future__ import print_function


import asyncio

from opentracing.mocktracer import MockTracer
from opentracing.scope_managers.asyncio import AsyncioScopeManager
from ..testcase import OpenTracingTestCase
from ..utils import stop_loop_when


class TestAsyncio(OpenTracingTestCase):
    def setUp(self):
        self.tracer = MockTracer(AsyncioScopeManager())
        self.loop = asyncio.get_event_loop()

    def test_main(self):
        # Start a Span and let the callback-chain
        # finish it when the task is done
        async def task():
            with self.tracer.start_active_span('one', finish_on_close=False):
                self.submit()

        self.loop.create_task(task())

        stop_loop_when(self.loop,
                       lambda: len(self.tracer.finished_spans()) == 1)
        self.loop.run_forever()

        spans = self.tracer.finished_spans()
        self.assertEqual(len(spans), 1)
        self.assertEqual(spans[0].operation_name, 'one')

        for i in range(1, 4):
            self.assertEqual(spans[0].tags.get('key%s' % i, None), str(i))

    def submit(self):
        span = self.tracer.scope_manager.active.span

        async def task1():
            with self.tracer.scope_manager.activate(span, False):
                span.set_tag('key1', '1')

                async def task2():
                    with self.tracer.scope_manager.activate(span, False):
                        span.set_tag('key2', '2')

                        async def task3():
                            with self.tracer.scope_manager.activate(span,
                                                                    False):
                                span.set_tag('key3', '3')
                                span.finish()

                        self.loop.create_task(task3())

                self.loop.create_task(task2())

        self.loop.create_task(task1())
