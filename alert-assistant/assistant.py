import requests
from datetime import datetime


PROMETHEUS_URL = "http://prometheus:9090"
LOKI_URL = "http://loki:3100"


def query_prometheus(query):
    """Query Prometheus and return the result."""

    url = f"{PROMETHEUS_URL}/api/v1/query"

    response = requests.get(
        url,
        params={"query": query},
        timeout=10
    )

    response.raise_for_status()

    return response.json()


def query_loki(query):
    """Query Loki for recent logs."""

    url = f"{LOKI_URL}/loki/api/v1/query_range"

    response = requests.get(
        url,
        params={
            "query": query,
            "limit": 20,
            "direction": "backward"
        },
        timeout=10
    )

    response.raise_for_status()

    return response.json()


def get_metrics():
    """Collect application metrics."""

    print("\n[1] Collecting Prometheus metrics...")

    request_count = query_prometheus(
        "api_requests_total"
    )

    error_count = query_prometheus(
        "api_errors_total"
    )

    return {
        "requests": request_count,
        "errors": error_count
    }


def get_logs():
    """Collect application error logs."""

    print("\n[2] Collecting Loki logs...")

    logs = query_loki(
        '{job="sample-app"} |= "ERROR"'
    )

    return logs


def analyze_incident():

    print("\n========================================")
    print("       GRAFANA ALERT ASSISTANT")
    print("========================================")

    print(
        f"Analysis time: {datetime.now()}"
    )

    # --------------------------------------------------
    # Collect metrics
    # --------------------------------------------------

    metrics = get_metrics()

    # --------------------------------------------------
    # Collect logs
    # --------------------------------------------------

    logs = get_logs()

    # --------------------------------------------------
    # Print evidence
    # --------------------------------------------------

    print("\n========================================")
    print("METRIC EVIDENCE")
    print("========================================")

    print(metrics)

    print("\n========================================")
    print("LOG EVIDENCE")
    print("========================================")

    print(logs)

    # --------------------------------------------------
    # Simple deterministic correlation
    # --------------------------------------------------

    print("\n========================================")
    print("INCIDENT ANALYSIS")
    print("========================================")

    if logs["data"]["result"]:

        print("Incident detected!")

        print(
            "Evidence: Application ERROR logs "
            "were found in Loki."
        )

        print(
            "Likely area: Database connectivity."
        )

    else:

        print("No application error logs detected.")

    print("\n========================================")


if __name__ == "__main__":

    analyze_incident()
