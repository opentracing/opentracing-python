.. :changelog:

History
-------

1.0rc4 (2016-05-21)
-------------------

- Add standard tags per http://opentracing.io/data-semantics/


1.0rc3 (2016-03-22)
-------------------

- No changes yet


1.0rc3 (2016-03-22)
-------------------

- Move to simpler carrier formats


1.0rc2 (2016-03-11)
-------------------

- Remove the Injector/Extractor layer


1.0rc1 (2016-02-24)
-------------------

- Upgrade to 1.0 RC specification


0.6.3 (2016-01-16)
------------------

- Rename repository back to opentracing-python


0.6.2 (2016-01-15)
------------------

- Validate chaining of logging calls


0.6.1 (2016-01-09)
------------------

- Fix typo in the attributes API test


0.6.0 (2016-01-09)
------------------

- Change inheritance to match api-go: TraceContextSource extends codecs,
Tracer extends TraceContextSource
- Create API harness


0.5.2 (2016-01-08)
------------------

- Update README and meta.


0.5.1 (2016-01-08)
------------------

- Prepare for PYPI publishing.


0.5.0 (2016-01-07)
------------------

- Remove debug flag
- Allow passing tags to start methods
- Add Span.add_tags() method


0.4.2 (2016-01-07)
------------------

- Add SPAN_KIND tag


0.4.0 (2016-01-06)
------------------

- Rename marshal -> encode


0.3.1 (2015-12-30)
------------------

- Fix std context implementation to refer to Trace Attributes instead of metadata


0.3.0 (2015-12-29)
------------------

- Rename trace tags to Trace Attributes. Rename RPC tags to PEER. Add README.


0.2.0 (2015-12-28)
------------------

- Export global `tracer` variable.


0.1.4 (2015-12-28)
------------------

- Rename RPC_SERVICE tag to make it symmetric


0.1.3 (2015-12-27)
------------------

- Allow repeated keys for span tags; add standard tag names for RPC


0.1.2 (2015-12-27)
------------------

- Move creation of child context to TraceContextSource


0.1.1 (2015-12-27)
------------------

- Add log methods


0.1.0 (2015-12-27)
------------------

- Initial public API

