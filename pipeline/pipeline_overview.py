"""
WindBorne pipeline overview — chunk 1.1
Not production code. Shows the shape of each stage: what comes in, what goes out, what breaks if it's wrong.
"""

PIPELINE = [
    {
        "stage": "1. Balloon",
        "input":  "Atmospheric sensor readings (pressure, temp, humidity, GPS)",
        "output": "Protobuf packet (~100-200 bytes)",
        "why_this_format": "Iridium charges per byte. Protobuf is 5-10x smaller than JSON.",
        "breaks_if": "Packet too large → Iridium drops it → gap in sequence numbers",
    },
    {
        "stage": "2. Iridium satellite",
        "input":  "Protobuf packet",
        "output": "HTTP POST to WindBorne ingestion endpoint",
        "why_this_format": "Only satellite network with near-global coverage at stratospheric altitudes",
        "breaks_if": "Satellite link congested or balloon out of view → packet loss → sequence gap",
    },
    {
        "stage": "3. HTTP ingestion endpoint",
        "input":  "HTTP POST with Protobuf body",
        "output": "Message produced to Kafka topic",
        "why_this_format": "Decouples ingestion from processing. Endpoint just acks and moves on.",
        "breaks_if": "Kafka unavailable → backpressure → HTTP endpoint starts rejecting → data loss",
    },
    {
        "stage": "4. Kafka topic",
        "input":  "Protobuf messages from all balloons",
        "output": "Ordered, durable log — consumers pull at their own pace",
        "why_this_format": "Absorbs bursts, survives consumer restarts, enables replay if QC logic changes",
        "breaks_if": "Consumer lag grows → latency into 10-min WeatherMesh window at risk",
    },
    {
        "stage": "5. Kafka consumer + QC",
        "input":  "Protobuf message",
        "output": "QC-annotated record (pass / flagged / rejected)",
        "why_this_format": "QC happens here — not at ingestion — so we can replay with fixed logic",
        "breaks_if": "Bug in QC silently rejects valid data → WeatherMesh gets sparse input → forecast degrades",
    },
    {
        "stage": "6a. ClickHouse (hot storage)",
        "input":  "QC-annotated record",
        "output": "Row in MergeTree table",
        "why_this_format": "Columnar — fast analytics queries. Ops, monitoring, debugging.",
        "breaks_if": "Row-by-row inserts → MergeTree merge storms → query performance collapses",
    },
    {
        "stage": "6b. S3 + NetCDF (cold storage)",
        "input":  "QC-annotated record",
        "output": "NetCDF file on S3",
        "why_this_format": "Multidimensional array format — exactly what WeatherMesh expects as model input",
        "breaks_if": "Write latency too high → NetCDF not ready when WeatherMesh pulls → missed assimilation window",
    },
    {
        "stage": "7. WeatherMesh",
        "input":  "NetCDF files from S3 (pulled every 10 min)",
        "output": "Global weather forecast",
        "why_this_format": "Transformer model — needs structured grid input, not raw telemetry",
        "breaks_if": "Stale or sparse NetCDF → forecast accuracy drops → customer impact",
    },
]

SIDE_STORES = [
    {
        "store": "Redis",
        "what":  "Live balloon state (current position, last-seen timestamp)",
        "why":   "O(1) reads. TTL auto-expires stale balloons. Not on forecast critical path.",
    },
    {
        "store": "Postgres",
        "what":  "Balloon registry + command queue",
        "why":   "Source of truth for which balloons exist and what instructions are queued.",
    },
]


def print_pipeline():
    print("=" * 60)
    print("WINDBORNE PIPELINE — STAGE BY STAGE")
    print("=" * 60)
    for s in PIPELINE:
        print(f"\n{s['stage']}")
        print(f"  IN:      {s['input']}")
        print(f"  OUT:     {s['output']}")
        print(f"  WHY:     {s['why_this_format']}")
        print(f"  BREAKS:  {s['breaks_if']}")

    print("\n" + "=" * 60)
    print("SIDE STORES (not on 10-min critical path)")
    print("=" * 60)
    for store in SIDE_STORES:
        print(f"\n{store['store']}")
        print(f"  WHAT: {store['what']}")
        print(f"  WHY:  {store['why']}")


if __name__ == "__main__":
    print_pipeline()
