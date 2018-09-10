from __future__ import print_function

from concurrent.futures import ThreadPoolExecutor
from flask import Flask

from opentracing.ext import tags
from opentracing.mocktracer import MockTracer
from opentracing.scope_managers.flask import FlaskScopeManager
from ..testcase import OpenTracingTestCase
from ..utils import get_logger, get_one_by_operation_name
from .request_handler import RequestHandler


logger = get_logger(__name__)


class Client(object):
    def __init__(self, request_handler, executor, app):
        self.request_handler = request_handler
        self.executor = executor
        self.app = app

    def send_task(self, message):
        request_context = {}

        def before_handler():
            with self.app.test_request_context():
                self.request_handler.before_request(message, request_context)

        def after_handler():
            with self.app.test_request_context():
                self.request_handler.after_request(message, request_context)

        self.executor.submit(before_handler).result()
        self.executor.submit(after_handler).result()

        return '%s::response' % message

    def send(self, message):
        return self.executor.submit(self.send_task, message)

    def send_sync(self, message, timeout=5.0):
        f = self.executor.submit(self.send_task, message)
        return f.result(timeout=timeout)


class TestFlask(OpenTracingTestCase):
    """
    There is only one instance of 'RequestHandler' per 'Client'. Methods of
    'RequestHandler' are executed concurrently in different threads which are
    reused (executor). Therefore we cannot use current active span and
    activate span. So one issue here is setting correct parent span.
    """

    def setUp(self):
        self.tracer = MockTracer()
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.app = Flask(__name__)
        self.client = Client(RequestHandler(self.tracer), self.executor, self.app)

    def test_two_callbacks(self):
        with self.app.test_request_context():
            response_future1 = self.client.send('message1')
            response_future2 = self.client.send('message2')

            self.assertEquals('message1::response', response_future1.result(5.0))
            self.assertEquals('message2::response', response_future2.result(5.0))

        spans = self.tracer.finished_spans()
        self.assertEquals(len(spans), 2)

        for span in spans:
            self.assertEquals(span.tags.get(tags.SPAN_KIND, None),
                              tags.SPAN_KIND_RPC_CLIENT)

        self.assertNotSameTrace(spans[0], spans[1])
        self.assertIsNone(spans[0].parent_id)
        self.assertIsNone(spans[1].parent_id)

    def test_parent_not_picked(self):
        """Active parent should not be picked up by child."""
        with self.app.test_request_context():
            with self.tracer.start_active_span('parent'):
                response = self.client.send_sync('no_parent')
                self.assertEquals('no_parent::response', response)

        spans = self.tracer.finished_spans()
        self.assertEquals(len(spans), 2)

        child_span = get_one_by_operation_name(spans, 'send')
        self.assertIsNotNone(child_span)

        parent_span = get_one_by_operation_name(spans, 'parent')
        self.assertIsNotNone(parent_span)

        # Here check that there is no parent-child relation.
        self.assertIsNotChildOf(child_span, parent_span)

    def test_bad_solution_to_set_parent(self):
        """Solution is bad because parent is per client
        (we don't have better choice)"""
        with self.app.test_request_context():
            with self.tracer.start_active_span('parent') as scope:
                client = Client(RequestHandler(self.tracer, scope.span.context),
                                self.executor, self.app)
                response = client.send_sync('correct_parent')
                self.assertEquals('correct_parent::response', response)

        response = client.send_sync('wrong_parent')
        self.assertEquals('wrong_parent::response', response)

        spans = self.tracer.finished_spans()
        self.assertEquals(len(spans), 3)

        spans = sorted(spans, key=lambda x: x.start_time)
        parent_span = get_one_by_operation_name(spans, 'parent')
        self.assertIsNotNone(parent_span)

        self.assertIsChildOf(spans[1], parent_span)
        self.assertIsChildOf(spans[2], parent_span)
