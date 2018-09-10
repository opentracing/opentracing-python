from __future__ import print_function

from threading import Thread
from six.moves import queue

from flask import Flask

import opentracing
from opentracing.ext import tags
from opentracing.mocktracer import MockTracer
from opentracing.scope_managers.flask import FlaskScopeManager
from ..testcase import OpenTracingTestCase
from ..utils import await_until, get_logger, get_one_by_tag


logger = get_logger(__name__)


class Server(Thread):
    def __init__(self, *args, **kwargs):
        tracer = kwargs.pop('tracer')
        queue = kwargs.pop('queue')
        app = kwargs.pop('app')
        super(Server, self).__init__(*args, **kwargs)

        self.daemon = True
        self.tracer = tracer
        self.queue = queue
        self.app = app

    def run(self):
        with self.app.test_request_context():
            value = self.queue.get()
            self.process(value)

    def process(self, message):
        logger.info('Processing message in server')

        ctx = self.tracer.extract(opentracing.Format.TEXT_MAP, message)
        with self.tracer.start_active_span('receive',
                                           child_of=ctx) as scope:
            scope.span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_SERVER)


class Client(object):
    def __init__(self, tracer, queue, app):
        self.tracer = tracer
        self.queue = queue
        self.app = app

    def send(self):
        with self.app.test_request_context():
            with self.tracer.start_active_span('send') as scope:
                scope.span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_CLIENT)

                message = {}
                self.tracer.inject(scope.span.context,
                                   opentracing.Format.TEXT_MAP,
                                   message)
                self.queue.put(message)

        logger.info('Sent message from client')


class TestFlask(OpenTracingTestCase):
    def setUp(self):
        self.tracer = MockTracer(FlaskScopeManager())
        self.queue = queue.Queue()
        self.app = Flask(__name__)
        self.server = Server(tracer=self.tracer, queue=self.queue, app=self.app)
        self.server.start()

    def test(self):
        client = Client(self.tracer, self.queue, self.app)
        client.send()

        await_until(lambda: len(self.tracer.finished_spans()) >= 2)

        spans = self.tracer.finished_spans()
        self.assertIsNotNone(get_one_by_tag(spans,
                                            tags.SPAN_KIND,
                                            tags.SPAN_KIND_RPC_SERVER))
        self.assertIsNotNone(get_one_by_tag(spans,
                                            tags.SPAN_KIND,
                                            tags.SPAN_KIND_RPC_CLIENT))
