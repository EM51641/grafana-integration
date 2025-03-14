# OpenTelemetry Getting Started

This project demonstrates how to set up a complete observability stack using OpenTelemetry, Grafana, Prometheus, Loki, and Tempo.

## Components

- **OpenTelemetry Collector**: Receives, processes, and exports telemetry data
- **Grafana**: Visualization and dashboarding
- **Prometheus**: Metrics storage and querying
- **Loki**: Log aggregation system
- **Tempo**: Distributed tracing backend
- **PostgreSQL**: Sample database for application data

## Setup Instructions

### Prerequisites

- Docker and Docker Compose
- Python 3.8+ (for the sample application)

### Running the Stack

1. Start the observability stack:

```bash
docker-compose up -d
```

2. Access Grafana at http://localhost:3000
   - Username: admin
   - Password: admin

3. Run your application with OpenTelemetry instrumentation:

```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Set up the tracer provider
tracer_provider = TracerProvider()
trace.set_tracer_provider(tracer_provider)

# Configure the OTLP exporter
otlp_exporter = OTLPSpanExporter(
    endpoint="localhost:4317",
    insecure=True
)

# Add the exporter to the tracer provider
tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

# Get a tracer
tracer = trace.get_tracer(__name__)

# Create spans in your application
with tracer.start_as_current_span("my_span") as span:
    span.set_attribute("custom.attribute", "value")
    # Your application code here
```

## Configuration Files

- `docker-compose.yml`: Defines all services and their configurations
- `otel-collector-config.yaml`: Configures the OpenTelemetry Collector
- `prometheus.yml`: Prometheus configuration
- `loki-config.yaml`: Loki configuration
- `tempo-config.yaml`: Tempo configuration

## Troubleshooting

If you encounter connection issues between services:

1. Check that all containers are running: `docker-compose ps`
2. Verify network connectivity: `docker network inspect monitoring`
3. Check service logs: `docker-compose logs -f [service_name]`

## License

MIT # grafana-integration
