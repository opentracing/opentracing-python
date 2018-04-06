class ResponseListener(object):
    def __init__(self, span):
        self.span = span

    def on_response(self, res):
        self.span.finish()
