from __future__ import print_function

import asyncio

from opentracing.ext import tags
from opentracing.mocktracer import MockTracer
from opentracing.scope_managers.contextvars import ContextVarsScopeManager
from ..testcase import OpenTracingTestCase
from ..utils import get_logger, get_one_by_operation_name, stop_loop_when
from .request_handler import RequestHandler


logger = get_logger(__name__)


class Client(object):
    def __init__(self, request_handler, loop):
        self.request_handler = request_handler
        self.loop = loop

    async def send_task(self, message):
        request_context = {}

        async def before_handler():
            self.request_handler.before_request(message, request_context)

        async def after_handler():
            self.request_handler.after_request(message, request_context)

        await before_handler()
        await after_handler()

        return '%s::response' % message

    def send(self, message):
        return self.send_task(message)

    def send_sync(self, message):
        return self.loop.run_until_complete(self.send_task(message))


class TestAsyncioContextVars(OpenTracingTestCase):
    """
    There is only one instance of 'RequestHandler' per 'Client'. Methods of
    'RequestHandler' are executed in different Tasks, but the context
    is the same, so we can leverage it for accessing the active span.
    """

    def setUp(self):
        self.tracer = MockTracer(ContextVarsScopeManager())
        self.loop = asyncio.get_event_loop()
        self.client = Client(RequestHandler(self.tracer), self.loop)

    def test_two_callbacks(self):
        res_future1 = self.loop.create_task(self.client.send('message1'))
        res_future2 = self.loop.create_task(self.client.send('message2'))

        stop_loop_when(self.loop,
                       lambda: len(self.tracer.finished_spans()) >= 2)
        self.loop.run_forever()

        self.assertEqual('message1::response', res_future1.result())
        self.assertEqual('message2::response', res_future2.result())

        spans = self.tracer.finished_spans()
        self.assertEqual(len(spans), 2)

        for span in spans:
            self.assertEqual(span.tags.get(tags.SPAN_KIND, None),
                             tags.SPAN_KIND_RPC_CLIENT)

        self.assertNotSameTrace(spans[0], spans[1])
        self.assertIsNone(spans[0].parent_id)
        self.assertIsNone(spans[1].parent_id)

    def test_parent_not_picked(self):
        """Active parent should not be picked up by child
        as we pass ignore_active_span=True to the RequestHandler"""

        async def do():
            with self.tracer.start_active_span('parent'):
                response = await self.client.send_task('no_parent')
                self.assertEqual('no_parent::response', response)

        self.loop.run_until_complete(do())

        spans = self.tracer.finished_spans()
        self.assertEqual(len(spans), 2)

        child_span = get_one_by_operation_name(spans, 'send')
        self.assertIsNotNone(child_span)

        parent_span = get_one_by_operation_name(spans, 'parent')
        self.assertIsNotNone(parent_span)

        # Here check that there is no parent-child relation.
        self.assertIsNotChildOf(child_span, parent_span)

    def test_good_solution_to_set_parent(self):
        """Solution is good because, though the RequestHandler being shared,
        the context will be properly detected."""

        with self.tracer.start_active_span('parent'):
            req_handler = RequestHandler(self.tracer,
                                         ignore_active_span=False)
            client = Client(req_handler, self.loop)
            response = client.send_sync('correct_parent')

            self.assertEqual('correct_parent::response', response)

        # Should NOT be a child of the previously activated Span
        response = client.send_sync('wrong_parent')
        self.assertEqual('wrong_parent::response', response)

        spans = self.tracer.finished_spans()
        self.assertEqual(len(spans), 3)

        spans = sorted(spans, key=lambda x: x.start_time)
        parent_span = get_one_by_operation_name(spans, 'parent')
        self.assertIsNotNone(parent_span)

        self.assertIsChildOf(spans[1], parent_span)
        self.assertIsNotChildOf(spans[2], parent_span)  # Proper parent (none).
