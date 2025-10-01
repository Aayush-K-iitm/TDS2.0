from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import json
import pathlib

app = FastAPI()

# Enable CORS for any origin, POST allowed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # allow all origins
    allow_methods=["*"],       # allow all methods (POST, GET, etc.)
    allow_headers=["*"],       # allow all headers
)

# Load telemetry data
DATA_PATH = pathlib.Path(__file__).parent.parent / "data" / "telemetry.json"
with open(DATA_PATH) as f:
    telemetry = json.load(f)

@app.post("/")
async def check_latency(req: Request):
    body = await req.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    result = {}
    for region in regions:
        records = telemetry.get(region, [])
        if not records:
            continue

        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime"] for r in records]

        avg_latency = float(np.mean(latencies))
        p95_latency = float(np.percentile(latencies, 95))
        avg_uptime = float(np.mean(uptimes))
        breaches = sum(1 for l in latencies if l > threshold)

        result[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches,
        }

    return result
