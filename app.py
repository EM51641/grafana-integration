from random import randint
from time import sleep
from flask import Flask, request
import logging
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
import concurrent.futures

# Import SQLAlchemy and its OpenTelemetry instrumentation
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

# Create a resource for OpenTelemetry
resource = Resource.create({
    "service.name": "bvx-rest-api",
    "environment": "development",
    "host.name": "local-dev"
})

logger_provider = LoggerProvider(resource=resource)

# set the providers

set_logger_provider(logger_provider)

exporter = OTLPLogExporter(endpoint="localhost:4317", insecure=True)

# add the batch processors to the trace provider
logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))

handler = LoggingHandler(level=logging.DEBUG,logger_provider=logger_provider)

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)  # Adjust the level appropriately.
root_logger.addHandler(handler)

# Set up metrics
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(
        endpoint="localhost:4317",
        insecure=True
    ),
    export_interval_millis=5000
)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)

# Set up tracing
tracer_provider = TracerProvider(resource=resource)
otlp_span_exporter = OTLPSpanExporter(
    endpoint="localhost:4317",
    insecure=True,
    timeout=30
)
tracer_provider.add_span_processor(BatchSpanProcessor(otlp_span_exporter))
trace.set_tracer_provider(tracer_provider)

# Create Flask app
app = Flask(__name__)
logger = logging.getLogger(__name__)

# Automatically instrument Flask
FlaskInstrumentor().instrument_app(app, meter_provider=meter_provider, tracer_provider=tracer_provider)

# --- SQLAlchemy Setup and Instrumentation ---

# Create a SQLAlchemy engine (using PostgreSQL in this example)
engine = create_engine(
    "postgresql://postgres:postgres@localhost:5432/testdb",
    echo=True,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True
)

# Instrument SQLAlchemy so that database calls are traced
SQLAlchemyInstrumentor().instrument(engine=engine, meter_provider=meter_provider, tracer_provider=tracer_provider)

# Define the base class for declarative models
Base = declarative_base()

# Create a simple model: a User table
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)

# Create tables if they don't already exist
Base.metadata.create_all(engine)

# Set up a SQLAlchemy session factory
SessionLocal = sessionmaker(bind=engine)

# Sample route that queries the database
@app.route("/users")
def get_users():
    session = SessionLocal()
    users = session.query(User).all()
    session.close()
    return {"users": [user.name for user in users]}

@app.route("/rolldice")
def roll_dice():
    player = request.args.get('player', default=None, type=str)
    result = roll()
    if player:
        logger.error("%s is rolling the dice: %s", player, result)
    else:
        logger.error("Anonymous player is rolling the dice: %s", result)
    return str(result)


@app.route("/error")
def error():
    raise Exception("This is a test error")


@app.route("/error_404")
def error_404():
    return "Not Found", 404

def roll():
    return randint(1, 6)

@app.route("/stress_test")
def stress_test():

    def make_query():
        session = SessionLocal()
        try:
            # First query
            sleep(2)
            users = session.query(User).all()
            # Second query to keep transaction open
            sleep(3)
            count = session.query(User).count()
            # Commit instead of rollback
            return len(users)
        finally:
            session.close()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(make_query) for _ in range(30)]
        results = [f.result() for f in futures]
    
    return {"concurrent_queries": len(results)}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)