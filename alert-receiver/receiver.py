import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, ValidationError


PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")
LOKI_URL = os.getenv("LOKI_URL", "http://loki:3100")


class Alert(BaseModel):
    model_config = ConfigDict(extra="allow")

    status: Optional[str] = None
    labels: Dict[str, Any] = {}
    annotations: Dict[str, Any] = {}
    startsAt: Optional[str] = None
    fingerprint: Optional[str] = None


class GrafanaWebhook(BaseModel):
    model_config = ConfigDict(extra="allow")

    status: Optional[str] = None
    alerts: List[Alert] = []
    groupLabels: Dict[str, Any] = {}
    commonLabels: Dict[str, Any] = {}
    commonAnnotations: Dict[str, Any] = {}


app = FastAPI(title="Grafana Alert Receiver")


def query_prometheus(query: str):
    """Query Prometheus and return the result."""

    response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": query},
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def query_loki(query: str):
    """Query Loki for recent logs."""

    response = requests.get(
        f"{LOKI_URL}/loki/api/v1/query_range",
        params={
            "query": query,
            "limit": 20,
            "direction": "backward",
        },
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def get_metrics():
    """Collect application metrics."""

    print("\n[1] Collecting Prometheus metrics...", flush=True)

    return {
        "requests": query_prometheus("api_requests_total"),
        "errors": query_prometheus("api_errors_total"),
    }


def get_logs():
    """Collect application error logs."""

    print("\n[2] Collecting Loki logs...", flush=True)

    return query_loki('{job="sample-app"} |= "ERROR"')


def analyze_incident() -> Dict[str, Any]:
    """Collect metrics and logs, print the evidence and return a summary."""

    print("\n========================================", flush=True)
    print("       GRAFANA ALERT ASSISTANT", flush=True)
    print("========================================", flush=True)
    print(f"Analysis time: {datetime.now()}", flush=True)

    try:
        metrics = get_metrics()
    except requests.RequestException as exc:
        print(f"Prometheus query failed: {exc}", flush=True)
        metrics = None

    try:
        logs = get_logs()
    except requests.RequestException as exc:
        print(f"Loki query failed: {exc}", flush=True)
        logs = None

    print("\n========================================", flush=True)
    print("METRIC EVIDENCE", flush=True)
    print("========================================", flush=True)
    print(metrics, flush=True)

    print("\n========================================", flush=True)
    print("LOG EVIDENCE", flush=True)
    print("========================================", flush=True)
    print(logs, flush=True)

    print("\n========================================", flush=True)
    print("INCIDENT ANALYSIS", flush=True)
    print("========================================", flush=True)

    error_logs_found = bool(
        logs and logs.get("data", {}).get("result")
    )

    if error_logs_found:
        print("Incident detected!", flush=True)
        print(
            "Evidence: Application ERROR logs were found in Loki.",
            flush=True,
        )
        print("Likely area: Database connectivity.", flush=True)
    else:
        print("No application error logs detected.", flush=True)

    print("\n========================================", flush=True)

    return {
        "metrics_collected": metrics is not None,
        "logs_collected": logs is not None,
        "error_logs_found": error_logs_found,
    }


def log_alert(alert: Alert) -> None:
    print("----------------------------------------", flush=True)
    print(f"status     : {alert.status}", flush=True)
    print(f"alertname  : {alert.labels.get('alertname')}", flush=True)
    print(f"severity   : {alert.labels.get('severity')}", flush=True)
    print(f"summary    : {alert.annotations.get('summary')}", flush=True)
    print(f"startsAt   : {alert.startsAt}", flush=True)
    print(f"fingerprint: {alert.fingerprint}", flush=True)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/alert")
async def receive_alert(request: Request):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Request body is not valid JSON",
        )

    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=400,
            detail="Grafana webhook payload must be a JSON object",
        )

    try:
        webhook = GrafanaWebhook.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=exc.errors())

    print("\n========== GRAFANA ALERT WEBHOOK ==========", flush=True)
    print(f"group status : {webhook.status}", flush=True)
    print(f"groupLabels  : {webhook.groupLabels}", flush=True)
    print(f"commonLabels : {webhook.commonLabels}", flush=True)
    print(f"commonAnnots : {webhook.commonAnnotations}", flush=True)

    for alert in webhook.alerts:
        log_alert(alert)

    firing = webhook.status == "firing" or any(
        alert.status == "firing" for alert in webhook.alerts
    )

    analysis = analyze_incident() if firing else None

    return JSONResponse(
        {
            "received": len(webhook.alerts),
            "status": webhook.status,
            "analysis": analysis,
        }
    )
