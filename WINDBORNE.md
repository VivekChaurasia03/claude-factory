# WindBorne — System Notes

WindBorne-specific architecture, products, and pipeline details.

---

## Full pipeline

```
Balloon (20km up)
  └─ Protobuf packet         [small — Iridium charges per byte]
       └─ Iridium satellite
            └─ HTTP endpoint [ingestion service — just produces to Kafka, no logic here]
                 └─ Kafka topic
                      └─ Kafka consumer  ← THIS is where all real work happens
                           ├─ QC checks
                           │    ├─ Plausibility    (is altitude physically possible?)
                           │    ├─ Persistence     (is a sensor stuck at the same value?)
                           │    ├─ Relational      (do pressure + altitude agree?)
                           │    └─ Spatial-temporal (did the balloon teleport?)
                           ├─ ClickHouse           [hot — ops, monitoring, analytics]
                           └─ S3 + NetCDF          [cold — WeatherMesh model input]
                                └─ WeatherMesh pulls every 10 min → forecast
                                     └─ Atlas API
                                          ├─ NOAA (raw observations only)
                                          └─ Energy traders, airlines (forecasts)
```

**Alongside the pipeline (not on critical path):**
- Redis — live balloon state (position, last-seen). O(1) reads, TTL auto-expires stale.
- Postgres — balloon registry (which balloons exist, queued commands).

---

## Key constraint
WeatherMesh assimilates every **10 minutes**. Every stage must complete inside that window.
Missing it = stale forecast = customer impact.

---

## ClickHouse vs S3/NetCDF — not the same
- **ClickHouse**: for *your* queries (ops dashboards, debugging, monitoring). Forecast still runs if this is slow — you're just blind.
- **S3/NetCDF**: what WeatherMesh actually consumes. If this breaks, the forecast breaks, even if ClickHouse looks healthy.

---

## Balloon packet fields

```
balloon_id, timestamp, lat, lon, altitude,
pressure (hPa), temp (°C), humidity (%),
battery_voltage, sequence_number
```

- **Lat/lon**: GPS
- **Altitude**: pressure sensor + barometric formula (NOT GPS — GPS altitude is unreliable at stratospheric heights)
- **Sequence gaps**: receive 104 then 107 → 105-106 were lost. Consumer must flag these.

---

## Two products, two customers

| Product | Customer | Notes |
|---|---|---|
| Observations API | NOAA | QC'd raw telemetry. NOAA feeds it into GFS (their own model). |
| WeatherMesh forecasts | Energy traders, airlines | NOAA does NOT buy forecasts — they have their own models. |

---

## WeatherMesh
- Transformer-based AI model (not physics-based NWP)
- Resolution: 0.25° global today, 3km work ongoing
- Speed: ~12 seconds on a single RTX 4090 — 100,000x faster than traditional NWP
- Pulls NetCDF from S3 every 10 min. Does NOT touch Kafka.
- Has access to all historical NetCDF files for model context.

---

## My ownership areas
- **Stage 3**: Kafka consumer → QC checks → ClickHouse (hot) + S3/NetCDF (cold)
- **Stage 5**: Atlas API serves WeatherMesh forecasts to customers

---

## QC checks (Stage 3)

Four checks run on every packet inside the Kafka consumer:

| Check | Stateful? | What it catches |
|---|---|---|
| Plausibility | No | Field outside physical bounds (altitude < -500m, temp > 60°C, etc.) |
| Relational | No | Pressure and altitude contradict each other (barometric formula, ±20% tolerance) |
| Persistence | Yes | Sensor stuck — same value for 5+ consecutive packets per balloon |
| Spatial-temporal | Yes | Balloon moved faster than 300 km/h between packets (haversine distance / elapsed time) |

**Stateful checks require a single QCChecker instance for the lifetime of the consumer process.** Creating a new instance per message resets per-balloon history — persistence and spatial-temporal checks stop working.

**QC failure policy:** Flag the packet (`qc_failed=True`), write to ClickHouse regardless (ops visibility), decision on S3/NetCDF write is a forecast-team call — not Stage 3's unilateral decision. Never drop silently.

**Barometric formula:** `altitude_m = 44330 * (1 - (pressure_hpa / 1013.25) ** 0.1903)`

---

## Kafka setup (local dev)

- Topic: `balloon-telemetry`
- Consumer group: `stage3-qc-pipeline`
- Partitioned by `balloon_id` — ordering guarantee per balloon
- `enable_auto_commit=False` — manual commit after processing (at-least-once)
- Consumer lag on `stage3-qc-pipeline` is the leading indicator for WeatherMesh window risk
- Docker: `apache/kafka:3.7.2` on port 9092, advertised on `host.docker.internal:9092` so Kafka UI container can reach it
- Kafka UI: `provectuslabs/kafka-ui` on port 8080
