from __future__ import print_function

import random

from tornado import gen, ioloop

from opentracing.mocktracer import MockTracer
from opentracing.scope_managers.tornado import TornadoScopeManager, \
        tracer_stack_context
from ..testcase import OpenTracingTestCase
from ..utils import get_logger, stop_loop_when


random.seed()
logger = get_logger(__name__)


class TestTornado(OpenTracingTestCase):
    def setUp(self):
        self.tracer = MockTracer(TornadoScopeManager())
        self.loop = ioloop.IOLoop.current()

    def test_main(self):
        @gen.coroutine
        def main_task():
            with self.tracer.start_active_span('parent'):
                tasks = self.submit_callbacks()
                yield tasks

        with tracer_stack_context():
            self.loop.add_callback(main_task)

        stop_loop_when(self.loop,
                       lambda: len(self.tracer.finished_spans()) == 4)
        self.loop.start()

        spans = self.tracer.finished_spans()
        self.assertEquals(len(spans), 4)
        self.assertNamesEqual(spans, ['task', 'task', 'task', 'parent'])

        for i in range(3):
            self.assertSameTrace(spans[i], spans[-1])
            self.assertIsChildOf(spans[i], spans[-1])

    @gen.coroutine
    def task(self, interval, parent_span):
        logger.info('Starting task')

        # NOTE: No need to reactivate the parent_span, as TracerStackContext
        # keeps track of it, BUT a limitation is that, yielding
        # upon multiple coroutines, we cannot mess with the context,
        # so no active span set here.
        assert self.tracer.active_span is not None
        with self.tracer.start_span('task'):
            yield gen.sleep(interval)

    def submit_callbacks(self):
        parent_span = self.tracer.scope_manager.active.span
        tasks = []
        for i in range(3):
            interval = 0.1 + random.randint(200, 500) * 0.001
            t = self.task(interval, parent_span)
            tasks.append(t)

        return tasks
