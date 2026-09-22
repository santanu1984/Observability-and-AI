from fastapi import FastAPI
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response
import time
import random
import logging


app = FastAPI()
DB_FAILURE = False

# -------------------------
# Logging configuration
# -------------------------

logging.basicConfig(
    filename="/app/logs/app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger(__name__)


# -------------------------
# Prometheus metrics
# -------------------------

REQUEST_COUNT = Counter(
    "api_requests_total",
    "Total API Requests"
)

REQUEST_TIME = Histogram(
    "api_response_time_seconds",
    "API Response Time"
)


# -------------------------
# Application endpoint
# -------------------------

@app.get("/")
def home():

    start_time = time.time()

    REQUEST_COUNT.inc()

    logger.info("Request received")

    if DB_FAILURE:

        logger.error(
            "Database connection timeout"
        )

        time.sleep(3)

        response_time = time.time() - start_time

        REQUEST_TIME.observe(response_time)

        return {
            "status": "error",
            "message": "Database timeout"
        }

    time.sleep(random.random())

    response_time = time.time() - start_time

    REQUEST_TIME.observe(response_time)

    logger.info(
        "Request completed response_time=%.3f",
        response_time
    )

    return {
        "message": "SRE Demo Application Running"
    }

@app.get("/simulate-db-failure")
def simulate_db_failure():

    global DB_FAILURE

    DB_FAILURE = True

    logger.error(
        "INCIDENT STARTED: Database failure simulation enabled"
    )

    return {
        "incident": "database_failure",
        "status": "ACTIVE"
    }
@app.get("/recover")
def recover():

    global DB_FAILURE

    DB_FAILURE = False

    logger.info(
        "INCIDENT RECOVERED: Database failure simulation disabled"
    )

    return {
        "incident": "database_failure",
        "status": "RECOVERED"
    }
# -------------------------
# Prometheus endpoint
# -------------------------

@app.get("/metrics")
def metrics():

    return Response(
        generate_latest(),
        media_type="text/plain"
    )
