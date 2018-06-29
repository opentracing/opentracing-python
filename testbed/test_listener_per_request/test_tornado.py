from __future__ import print_function

import functools

from tornado import gen, ioloop

from opentracing.ext import tags
from opentracing.mocktracer import MockTracer
from opentracing.scope_managers.tornado import TornadoScopeManager
from ..testcase import OpenTracingTestCase
from ..utils import get_one_by_tag

from .response_listener import ResponseListener


class Client(object):
    def __init__(self, tracer, loop):
        self.tracer = tracer
        self.loop = loop

    @gen.coroutine
    def task(self, message, listener):
        res = '%s::response' % message
        listener.on_response(res)
        return res

    def send_sync(self, message):
        span = self.tracer.start_span('send')
        span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_CLIENT)

        listener = ResponseListener(span)
        task_func = functools.partial(self.task, message, listener)
        return self.loop.run_sync(task_func)


class TestTornado(OpenTracingTestCase):
    def setUp(self):
        self.tracer = MockTracer(TornadoScopeManager())
        self.loop = ioloop.IOLoop.current()

    def test_main(self):
        client = Client(self.tracer, self.loop)
        res = client.send_sync('message')
        self.assertEquals(res, 'message::response')

        spans = self.tracer.finished_spans()
        self.assertEqual(len(spans), 1)

        span = get_one_by_tag(spans, tags.SPAN_KIND, tags.SPAN_KIND_RPC_CLIENT)
        self.assertIsNotNone(span)
