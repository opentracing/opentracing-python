import unittest


class OpenTracingTestCase(unittest.TestCase):
    def assertSameTrace(self, spanA, spanB):
        return self.assertEqual(spanA.context.trace_id,
                                spanB.context.trace_id)

    def assertNotSameTrace(self, spanA, spanB):
        return self.assertNotEqual(spanA.context.trace_id,
                                   spanB.context.trace_id)

    def assertIsChildOf(self, spanA, spanB):
        return self.assertEqual(spanA.parent_id, spanB.context.span_id)

    def assertIsNotChildOf(self, spanA, spanB):
        return self.assertNotEqual(spanA.parent_id, spanB.context.span_id)

    def assertNamesEqual(self, spans, names):
        self.assertEqual(list(map(lambda x: x.operation_name, spans)), names)
