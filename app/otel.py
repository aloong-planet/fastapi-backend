import opentelemetry.trace as otel_trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (OTLPSpanExporter as
                                                                   OTLPSpanExporterGRPC)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (OTLPSpanExporter as
                                                                   OTLPSpanExporterHTTP)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource


class OTELInstrumentInitializer:

    def __init__(self, service_name) -> None:
        self.resource = Resource(attributes={"service.name": service_name})

    def init_trace_provider(self, mode: str, endpoint: str) -> TracerProvider:
        tracer = TracerProvider(resource=self.resource)
        otel_trace.set_tracer_provider(tracer)

        if mode == "GRPC":
            tracer.add_span_processor(
                BatchSpanProcessor(OTLPSpanExporterGRPC(endpoint=endpoint, insecure=True)))
        elif mode == "HTTP":
            tracer.add_span_processor(BatchSpanProcessor(OTLPSpanExporterHTTP(endpoint=endpoint)))
        else:
            tracer.add_span_processor(
                BatchSpanProcessor(OTLPSpanExporterGRPC(endpoint=endpoint, insecure=True)))

        return tracer
