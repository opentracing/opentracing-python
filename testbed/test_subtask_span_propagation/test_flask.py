from __future__ import absolute_import, print_function

from concurrent.futures import ThreadPoolExecutor
from flask import Flask

from opentracing.scope_managers.flask import FlaskScopeManager
from opentracing.mocktracer import MockTracer
from ..testcase import OpenTracingTestCase


class TestFlask(OpenTracingTestCase):
    def setUp(self):
        self.tracer = MockTracer(FlaskScopeManager())
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.app = Flask(__name__)

    def test_main(self):
        res = self.executor.submit(self.parent_task, 'message').result()
        self.assertEqual(res, 'message::response')

        spans = self.tracer.finished_spans()
        self.assertEqual(len(spans), 2)
        self.assertNamesEqual(spans, ['child', 'parent'])
        self.assertIsChildOf(spans[0], spans[1])

    def parent_task(self, message):
        with self.app.test_request_context():
            with self.tracer.start_active_span('parent') as scope:
                f = self.executor.submit(self.child_task, message, scope.span)
                res = f.result()

        return res

    def child_task(self, message, span):
        with self.app.test_request_context():
            with self.tracer.scope_manager.activate(span, False):
                with self.tracer.start_active_span('child'):
                    return '%s::response' % message
