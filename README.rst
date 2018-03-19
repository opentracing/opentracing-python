OpenTracing API for Python
==========================

|GitterChat| |BuildStatus| |PyPI|

This library is a Python platform API for OpenTracing.

Required Reading
----------------

In order to understand the Python platform API, one must first be familiar with
the `OpenTracing project <http://opentracing.io>`_ and
`terminology <http://opentracing.io/documentation/pages/spec.html>`_ more
specifically.

Status
------

In the current version, ``opentracing-python`` provides only the API and a
basic no-op implementation that can be used by instrumentation libraries to
collect and propagate distributed tracing context.

Future versions will include a reference implementation utilizing an
abstract Recorder interface, as well as a
`Zipkin <http://openzipkin.github.io>`_-compatible Tracer.

Usage
-----

The work of instrumentation libraries generally consists of three steps:

1. When a service receives a new request (over HTTP or some other protocol),
   it uses OpenTracing's inject/extract API to continue an active trace, creating a
   Span object in the process. If the request does not contain an active trace,
   the service starts a new trace and a new *root* Span.
2. The service needs to store the current Span in some request-local storage,
   where it can be retrieved from when a child Span must be created, e.g. in case
   of the service making an RPC to another service.
3. When making outbound calls to another service, the current Span must be
   retrieved from request-local storage, a child span must be created (e.g., by
   using the ``start_child_span()`` helper), and that child span must be embedded
   into the outbound request (e.g., using HTTP headers) via OpenTracing's
   inject/extract API.

Below are the code examples for steps 1 and 3. Implementation of request-local
storage needed for step 2 is specific to the service and/or frameworks /
instrumentation libraries it is using (TODO: reference to other OSS projects
with examples of instrumentation).

Inbound request
^^^^^^^^^^^^^^^

Somewhere in your server's request handler code:

.. code-block:: python

   def handle_request(request):
       span = before_request(request, opentracing.tracer)
       # use span as Context Manager to ensure span.finish() will be called
       with span:
           # store span in some request-local storage
           with RequestContext(span):
               # actual business logic
               handle_request_for_real(request)


   def before_request(request, tracer):
       span_context = tracer.extract(
           format=Format.HTTP_HEADERS,
           carrier=request.headers,
       )
       span = tracer.start_span(
           operation_name=request.operation,
           child_of(span_context))
       span.set_tag('http.url', request.full_url)

       remote_ip = request.remote_ip
       if remote_ip:
           span.set_tag(tags.PEER_HOST_IPV4, remote_ip)

       caller_name = request.caller_name
       if caller_name:
           span.set_tag(tags.PEER_SERVICE, caller_name)

       remote_port = request.remote_port
       if remote_port:
           span.set_tag(tags.PEER_PORT, remote_port)

       return span

Outbound request
----------------

Somewhere in your service that's about to make an outgoing call:

.. code-block:: python

   from opentracing.ext import tags
   from opentracing.propagation import Format
   from opentracing_instrumentation import request_context

   from opentracing.ext import tags
   from opentracing.propagation import Format
   from opentracing_instrumentation import request_context

   # create and serialize a child span and use it as context manager
   with before_http_request(
       request=out_request,
       current_span_extractor=request_context.get_current_span):

       # actual call
       return urllib2.urlopen(request)


   def before_http_request(request, current_span_extractor):
       op = request.operation
       parent_span = current_span_extractor()
       outbound_span = opentracing.tracer.start_span(
           operation_name=op,
           child_of=parent_span
       )

       outbound_span.set_tag('http.url', request.full_url)
       service_name = request.service_name
       host, port = request.host_port
       if service_name:
           outbound_span.set_tag(tags.PEER_SERVICE, service_name)
       if host:
           outbound_span.set_tag(tags.PEER_HOST_IPV4, host)
       if port:
           outbound_span.set_tag(tags.PEER_PORT, port)

       http_header_carrier = {}
       opentracing.tracer.inject(
           span_context=outbound_span,
           format=Format.HTTP_HEADERS,
           carrier=http_header_carrier)

       for key, value in http_header_carrier.iteritems():
           request.add_header(key, value)

       return outbound_span

Development
-----------

Tests
^^^^^

.. code-block:: sh

   virtualenv env
   . ./env/bin/activate
   make bootstrap
   make test

Documentation
^^^^^^^^^^^^^

.. code-block:: sh

   virtualenv env
   . ./env/bin/activate
   make bootstrap
   make docs

The documentation is written to *docs/_build/html*.

LICENSE
^^^^^^^

[MIT License](./LICENSE).

Releases
^^^^^^^^

Before new release, add a summary of changes since last version to CHANGELOG.rst

.. code-block:: sh

   pip install zest.releaser[recommended]
   prerelease
   release
   git push origin master --follow-tags
   python setup.py sdist upload -r pypi upload_docs -r pypi
   postrelease
   git push

.. |GitterChat| image:: http://img.shields.io/badge/gitter-join%20chat%20%E2%86%92-brightgreen.svg
   :target: https://gitter.im/opentracing/public
.. |BuildStatus| image:: https://travis-ci.org/opentracing/opentracing-python.svg?branch-master
   :target: https://travis-ci.org/opentracing/opentracing-python
.. |PyPI| image:: https://badge.fury.io/py/opentracing.svg
   :target: https://badge.fury.io/py/opentracing


