# Observability-and-AI / Grafana Alert Assistant

An end-to-end AI-assisted Observability and Incident Correlation Stack built with **FastAPI**, **Prometheus**, **Grafana**, **Loki**, **Promtail**, and automated **Alert Assistant / Receiver** services.

---

## 🏗️ Architecture & Services

| Service | Host Port | In-Cluster Port / Target | Description |
| :--- | :---: | :---: | :--- |
| **Sample App** | `8000` | `http://sample-app:8000` | FastAPI demo application generating metrics and log entries |
| **Alert Receiver** | `8001` | `http://alert-receiver:8000` | Webhook endpoint receiving Grafana alerts & running log/metric correlation |
| **Grafana** | `3000` | `http://grafana:3000` | Observability dashboards & alert management |
| **Prometheus** | `9090` | `http://prometheus:9090` | Metrics collection and storage |
| **Loki** | `3100` | `http://loki:3100` | Log aggregation engine |
| **Promtail** | — | — | Log shipper sending sample application logs to Loki |
| **Alert Assistant** | — | — | One-shot incident correlation runner |

---

## 🚀 Quick Start Guide (How to Run)

### 1. Prerequisites
Ensure you have **Docker** and **Docker Compose** installed and running on your system.

### 2. Pull Latest Code
```bash
git pull origin main
```

### 3. Build & Start All Services
Run the following command from the root directory of the project:
```bash
docker compose up -d --build
```

### 4. Verify Running Containers
Check that all containers are active and healthy:
```bash
docker compose ps
```

---

## 🧪 Testing & Simulating Incidents

### 1. Access Sample Application
```bash
curl http://localhost:8000/
```
Or open [http://localhost:8000](http://localhost:8000) in your browser.

### 2. Simulate Database Failure Incident
Trigger a simulated incident to generate error metrics and logs:
```bash
curl http://localhost:8000/simulate-db-failure
```

Send a few requests to generate error logs in Loki:
```bash
curl http://localhost:8000/
```

### 3. Recover from Incident
Turn off the simulated database failure:
```bash
curl http://localhost:8000/recover
```

---

## 🔔 Testing Alert Receiver Webhook

You can trigger the webhook manually using `curl`:

```bash
curl -X POST http://localhost:8001/alert \
  -H 'Content-Type: application/json' \
  -d '{
    "status": "firing",
    "groupLabels": {"alertname": "HighErrorRate"},
    "commonLabels": {"alertname": "HighErrorRate", "severity": "critical"},
    "commonAnnotations": {"summary": "API error rate is above threshold"},
    "alerts": [
      {
        "status": "firing",
        "labels": {"alertname": "HighErrorRate", "severity": "critical"},
        "annotations": {"summary": "API error rate is above threshold"},
        "startsAt": "2026-01-01T00:00:00Z",
        "fingerprint": "abc123def456"
      }
    ]
  }'
```

View the receiver logs to see the correlated metric & log evidence:
```bash
docker compose logs -f alert-receiver
```

---

## ⚙️ Configuring Webhooks in Grafana

For step-by-step instructions on wiring Grafana alert contact points to `alert-receiver`, see [docs/alert-receiver-setup.md](docs/alert-receiver-setup.md).

---

## 🛑 Stopping the Project

To stop and remove all running containers and networks:
```bash
docker compose down
```
