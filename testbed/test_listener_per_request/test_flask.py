from __future__ import print_function

from concurrent.futures import ThreadPoolExecutor
from flask import Flask

from opentracing.ext import tags
from opentracing.mocktracer import MockTracer
from opentracing.scope_managers.flask import FlaskScopeManager
from ..testcase import OpenTracingTestCase
from ..utils import get_one_by_tag

from .response_listener import ResponseListener


class Client(object):
    def __init__(self, tracer):
        self.tracer = tracer
        self.executor = ThreadPoolExecutor(max_workers=3)

    def _task(self, message, listener):
        res = '%s::response' % message
        listener.on_response(res)
        return res

    def send_sync(self, message):
        span = self.tracer.start_span('send')
        span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_CLIENT)

        listener = ResponseListener(span)
        return self.executor.submit(self._task, message, listener).result()


class TestFlask(OpenTracingTestCase):
    def setUp(self):
        self.tracer = MockTracer(FlaskScopeManager())
        self.app = Flask(__name__)

    def test_main(self):
        with self.app.test_request_context():
            client = Client(self.tracer)
            res = client.send_sync('message')
            self.assertEquals(res, 'message::response')

            spans = self.tracer.finished_spans()
            self.assertEqual(len(spans), 1)

        span = get_one_by_tag(spans, tags.SPAN_KIND, tags.SPAN_KIND_RPC_CLIENT)
        self.assertIsNotNone(span)
