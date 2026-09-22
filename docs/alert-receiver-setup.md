# Alert Receiver Setup

The `alert-receiver` service is a FastAPI app that accepts Grafana alert webhook
notifications and runs the same Prometheus/Loki evidence collection as
`alert-assistant`.

- Container: `alert-receiver`
- In-cluster URL (other compose services): `http://alert-receiver:8000`
- Host URL: `http://localhost:8001`

Endpoints:

| Method | Path      | Description                                        |
| ------ | --------- | -------------------------------------------------- |
| GET    | `/health` | Liveness check, returns `{"status": "ok"}`          |
| POST   | `/alert`  | Grafana webhook receiver; runs analysis on `firing` |

Start the stack:

```bash
docker compose up --build
```

## Wire it up in Grafana

Verified against Grafana 13.2.2 (the version `grafana/grafana` currently pulls);
menu names differ in older versions.

1. Open Grafana at http://localhost:3000.
2. Go to **Alerting → Notification configuration → Contact points → + New
   contact point**.
3. Name it `alert-receiver`, integration **Webhook**.
4. URL: `http://alert-receiver:8000/alert` (Grafana reaches the receiver by its
   compose service name; do not use `localhost` here).
5. Under **Optional Webhook settings**, set HTTP Method to `POST`. No
   authentication is required.
6. **Save contact point**. To send a sample notification, reopen the contact
   point with **Edit** and use **Test → Send test notification**.
7. Attach it to alerts either by:
   - **Alerting → Notification configuration → Notification policies** → edit
     the default policy (or add a child route) and set the contact point to
     `alert-receiver`, or
   - editing an alert rule and selecting `alert-receiver` under
     **Configure notifications**.

Watch the output with:

```bash
docker compose logs -f alert-receiver
```

## Local test with curl

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

The response summarises what was received and whether error logs were found; the
full metric/log evidence and incident analysis are printed to the container logs.

Note: `sample-app` exports `api_requests_total` but no error counter, so the
`api_errors_total` query (kept for parity with `alert-assistant`) always returns
an empty result. `metrics_collected: true` only means the queries succeeded, not
that both series exist.

A payload with `"status": "resolved"` is logged but skips the analysis. Malformed
bodies (invalid JSON, or a non-object payload) return `400` with a `detail`
message.
