"""
FraudShield Prometheus Telemetry and Observability Metrics.
"""

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from starlette.responses import Response

# HTTP API metrics
HTTP_REQUESTS_TOTAL = Counter(
    "fraudshield_http_requests_total",
    "Total incoming HTTP requests",
    ["method", "endpoint", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "fraudshield_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

# Machine Learning & Risk metrics
PREDICTIONS_TOTAL = Counter(
    "fraudshield_predictions_total",
    "Total fraud predictions evaluated",
    ["model_version", "predicted_class", "risk_level"],
)

PREDICTION_LATENCY_SECONDS = Histogram(
    "fraudshield_prediction_latency_seconds",
    "ML model inference and SHAP attribution duration in seconds",
    ["model_version"],
    buckets=[0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5],
)

ACTIVE_MODEL_VERSION = Gauge(
    "fraudshield_active_model_info",
    "Current active champion model version",
    ["version", "model_name"],
)


def metrics_endpoint() -> Response:
    """Exposes Prometheus text-formatted telemetry metrics."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

