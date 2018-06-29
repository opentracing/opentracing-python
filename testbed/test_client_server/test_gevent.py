from __future__ import print_function


import gevent
import gevent.queue

import opentracing
from opentracing.ext import tags
from opentracing.mocktracer import MockTracer
from opentracing.scope_managers.gevent import GeventScopeManager
from ..testcase import OpenTracingTestCase
from ..utils import get_logger, get_one_by_tag


logger = get_logger(__name__)


class Server(object):
    def __init__(self, *args, **kwargs):
        tracer = kwargs.pop('tracer')
        queue = kwargs.pop('queue')
        super(Server, self).__init__(*args, **kwargs)

        self.tracer = tracer
        self.queue = queue

    def run(self):
        value = self.queue.get()
        self.process(value)

    def process(self, message):
        logger.info('Processing message in server')

        ctx = self.tracer.extract(opentracing.Format.TEXT_MAP, message)
        with self.tracer.start_active_span('receive',
                                           child_of=ctx) as scope:
            scope.span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_SERVER)


class Client(object):
    def __init__(self, tracer, queue):
        self.tracer = tracer
        self.queue = queue

    def send(self):
        with self.tracer.start_active_span('send') as scope:
            scope.span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_CLIENT)

            message = {}
            self.tracer.inject(scope.span.context,
                               opentracing.Format.TEXT_MAP,
                               message)
            self.queue.put(message)

        logger.info('Sent message from client')


class TestGevent(OpenTracingTestCase):
    def setUp(self):
        self.tracer = MockTracer(GeventScopeManager())
        self.queue = gevent.queue.Queue()
        self.server = Server(tracer=self.tracer, queue=self.queue)

    def test(self):
        client = Client(self.tracer, self.queue)
        gevent.spawn(self.server.run)
        gevent.spawn(client.send)

        gevent.wait(timeout=5.0)

        spans = self.tracer.finished_spans()
        self.assertIsNotNone(get_one_by_tag(spans,
                                            tags.SPAN_KIND,
                                            tags.SPAN_KIND_RPC_SERVER))
        self.assertIsNotNone(get_one_by_tag(spans,
                                            tags.SPAN_KIND,
                                            tags.SPAN_KIND_RPC_CLIENT))
