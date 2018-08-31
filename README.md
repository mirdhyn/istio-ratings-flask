# Application-level tracing experiment with Istio
Testing application-level tracing with OpenCensus and OpenTracing libraries of a python (flask) rewrite of Istio's demo `ratings` service.

## with OpenCensus
OpenCensus python library is currently missing the B3 propagation that Istio is using.
A PR is under review to add B3 headers propagation: https://github.com/census-instrumentation/opencensus-python/pull/265

## with OpenTracing
Works as expected.
