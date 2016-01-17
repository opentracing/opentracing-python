# OpenTracing API for Python

This library is a Python platform API for OpenTracing.

## Required Reading

In order to understand the Python platform API, one must first be familiar with
the [OpenTracing project](http://opentracing.io) and
[terminology](http://opentracing.io/spec/) more generally.

## Status

In the current version, `api-python` provides only the API and a 
basic no-op implementation that can be used by instrumentation libraries to 
collect and propagate distributed tracing context.

Future versions will include a reference implementation utilizing an 
abstract Recorder interface, as well as a 
[Zipkin](http://openzipkin.github.io)-compatible Tracer.

## Usage

The work of instrumentation libraries generally consists of three steps:

1. When a service receives a new request (over HTTP or some other protocol),
it uses OpenTracing API serialization tools to extract a Trace Context 
from the request headers and create a Span object. If the request does
not contain a trace context, the service starts a new trace and a new 
*root* Span.
2. The service needs to store the current Span in some request-local storage,
where it can be retrieved from when a child Span must be created, e.g. in 
case of the service making an RPC to another service.
3. When making outbound calls to another service, the current Span must be 
retrieved from request-local storage, a child span must be created using
`span.start_child()` method, and the Trace Context of the child span must
be serialized into the outbound request (e.g. HTTP headers) using 
OpenTracing API serialization tools.

Below are the code examples for steps 1 and 3. Implementation of 
request-local storage needed for step 2 is specific to the service and/or 
frameworks / instrumentation libraries it is using (TODO reference to other
OSS projects with examples of instrumentation).

### Inbound request

Somewhere in your server's request handler code:

```python

    def handle_request(request):
        span = before_request(request, opentracing.tracer)
        # use span as Context Manager to ensure span.finish() will be called
        with span:
            # store span in some request-local storage
            with RequestContext(span):
                # actual business logic
                handle_request_for_real(request)
        
    
    def before_request(request, tracer):
        context = tracer.trace_context_from_text(
            trace_context_id=request.headers, 
            trace_attributes=request.headers
        )
        operation = request.operation
        if context is None:
            span = tracer.start_trace(operation_name=operation)
        else:
            span = tracer.join_trace(operation_name=operation,
                                     parent_trace_context=context)
    
        span.add_tag('client.http.url', request.full_url)
    
        remote_ip = request.remote_ip
        if remote_ip:
            span.add_tag(tags.PEER_HOST_IPV4, remote_ip)
    
        caller_name = request.caller_name
        if caller_name:
            span.add_tag(tags.PEER_SERVICE, caller_name)
    
        remote_port = request.remote_port
        if remote_port:
            span.add_tag(tags.PEER_PORT, remote_port)
    
        return span
```

### Outbound request

Somewhere in your service that's about to make an outgoing call:

```python

    # create and serialize a child span and use it as context manager
    with before_http_request(
        request=out_request,
        current_span_extractor=RequestContext.get_current_span):
    
        # actual call
        return urllib2.urlopen(request)
    
    
    def before_http_request(request, current_span_extractor):
        op = request.operation
        parent_span = current_span_extractor()
        if parent_span is None:
            span = opentracing.tracer.start_trace(operation_name=op)
        else:
            span = parent_span.start_child(operation_name=op)
    
        span.add_tag('server.http.url', request.full_url)
        service_name = request.service_name
        host, port = request.host_port
        if service_name:
            span.add_tag(tags.PEER_SERVICE, service_name)
        if host:
            span.add_tag(tags.PEER_HOST_IPV4, host)
        if port:
            span.add_tag(tags.PEER_PORT, port)
    
        h_ctx, h_attr = opentracing.tracer.trace_context_to_text(
            trace_context=span.trace_context)
        for key, value in h_ctx.iteritems():
            request.add_header(key, value)
        if h_attr:
            for key, value in h_attr.iteritems():
                request.add_header(key, value)
    
        return span
```

# Development

## Tests

```
virtualenv env
source env/bin/activate
make bootstrap
make test
```

## Releases

Before new release, add a summary of changes since last version to CHANGELOG.rst

```
pip install zest.releaser[recommended]
prerelease
release
git push origin master --follow-tags
python setup.py sdist upload -r pypi
postrelease
git push
```

