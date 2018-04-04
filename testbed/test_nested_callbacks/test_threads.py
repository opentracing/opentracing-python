from __future__ import print_function

from concurrent.futures import ThreadPoolExecutor

from opentracing.mocktracer import MockTracer
from ..testcase import OpenTracingTestCase
from ..utils import await_until


class TestThreads(OpenTracingTestCase):
    def setUp(self):
        self.tracer = MockTracer()
        self.executor = ThreadPoolExecutor(max_workers=3)

    def tearDown(self):
        self.executor.shutdown(False)

    def test_main(self):
        # Start a Span and let the callback-chain
        # finish it when the task is done
        with self.tracer.start_active_span('one', finish_on_close=False):
            self.submit()

        # Cannot shutdown the executor and wait for the callbacks
        # to be run, as in such case only the first will be executed,
        # and the rest will get canceled.
        await_until(lambda: len(self.tracer.finished_spans()) == 1, 5)

        spans = self.tracer.finished_spans()
        self.assertEqual(len(spans), 1)
        self.assertEqual(spans[0].operation_name, 'one')

        for i in range(1, 4):
            self.assertEqual(spans[0].tags.get('key%s' % i, None), str(i))

    def submit(self):
        span = self.tracer.scope_manager.active.span

        def task1():
            with self.tracer.scope_manager.activate(span, False):
                span.set_tag('key1', '1')

                def task2():
                    with self.tracer.scope_manager.activate(span, False):
                        span.set_tag('key2', '2')

                        def task3():
                            with self.tracer.scope_manager.activate(span,
                                                                    True):
                                span.set_tag('key3', '3')

                        self.executor.submit(task3)

                self.executor.submit(task2)

        self.executor.submit(task1)
