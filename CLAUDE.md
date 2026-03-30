# WindBorne Learning Environment — Vivek Chaurasia

## Environment
- OS: Windows 11, shell: PowerShell
- Multi-line bash commands (with `\` continuation) do NOT work — always give single-line PowerShell commands or use PowerShell backtick (`` ` ``) continuation
- Docker Desktop is installed and running

## Who I am
- Incoming Backend Engineer at WindBorne Systems (Palo Alto, CA)
- Manager: Kai Marshland (Co-Founder/CPO)
- Background: Tesla SDE intern — asyncio + Kafka + ClickHouse pipeline (660 metrics/sec), 400+ device real-time monitoring, token race condition fix
- Stack: Python, asyncio, FastAPI, Kafka, ClickHouse, PostgreSQL, Redis, React, Next.js, Docker, Rust (intermediate)

## Purpose of this repo
Pre-joining learning environment. Build real things to understand WindBorne's systems before day 1.
Goal: contributing on day 1, not exploring.

---

## How to tutor me
- Concept first (3-5 sentences), then a small runnable exercise
- Grug brain: simple > elegant, no unnecessary abstractions
- Correct me immediately if I'm wrong — don't let it slide
- Tesla analogies welcome where relevant
- After each exercise, ask one check question before moving on

---

## Kai's rules (internalize these)
- Grug brain: complexity is the enemy (grugbrain.dev)
- Velocity is #1 — ship something small early
- Never let a deadline slip silently
- Push info proactively — don't wait to be asked
- Local is a lie — think concurrent production instances always

---

## WindBorne — my ownership areas
- Stage 3: Kafka consumer → QC checks → ClickHouse (hot) + S3/NetCDF (cold)
- Stage 5: Atlas API serves WeatherMesh forecasts to customers

---

## Full pipeline (mental model)
```
Balloon → Protobuf → Iridium satellite → HTTP endpoint
HTTP endpoint → Kafka topic
Kafka consumer → QC → ClickHouse (analytics) + S3/NetCDF (cold)
WeatherMesh pulls NetCDF every 10 min → forecast
Atlas API → energy traders, airlines, NOAA (obs only)
```

Live state also flows to Redis (current balloon state, O(1) reads, TTL auto-expires stale balloons)
and Postgres (balloon registry + commands).

## The flywheel
Better balloons → better assimilation data → better forecasts → more customers → funds more balloons.
Every pipeline decision either helps or hurts this.

---

## Key technical facts

### Wire & storage formats
- Wire format: Protobuf (not JSON, not NetCDF — too heavy for Iridium)
- Cold storage / model input: NetCDF (variables + global attributes)

### ClickHouse
- Engine: MergeTree, columnar — batch inserts are critical, avoid row-by-row writes

### Kafka
- Durable log — supports replay via consumer offset reset

### QC checks
- Plausibility, persistence, relational, spatial-temporal

### Altitude
- Lat/lon: GPS
- Altitude: pressure sensor + barometric formula (not GPS)

### WeatherMesh assimilation window
- Every 10 minutes — missed window = stale forecast

---

## WeatherMesh — what it actually is
- Transformer-based AI model (not traditional NWP/physics-based)
- Current resolution: 0.25° global; target: arbitrary resolution (3km work ongoing)
- Speed: ~12 seconds on a single RTX 4090 — 100,000x faster than traditional NWP
- Accuracy: outperformed Google GraphCast by 11% on key forecasting metrics
- Hard latency constraint: assimilates every 10 min → my pipeline must deliver inside that window

---

## Two products, two customer types
| Product | Who buys it | Notes |
|---|---|---|
| Observations API | NOAA | QC'd raw telemetry; NOAA feeds it into their own GFS model |
| WeatherMesh forecasts | Energy traders, airlines, commercial | NOAA does NOT buy forecasts — they have their own models |

---

## Balloon packet fields
```
balloon_id, timestamp, lat, lon, altitude,
pressure (hPa), temp (°C), humidity (%),
battery_voltage, sequence_number
```
Sequence gaps matter: receive 104 then 107 → 105-106 were lost → flag as missing.

---

## Session tracking
- `notes/` — one file per completed chunk (e.g. `notes/1.1.md`). Written by `/done`. This is the source of truth for what's been covered.
- `LEARN.md` — general concepts (Kafka, ClickHouse, Protobuf, NetCDF, etc.) accumulated across sessions.
- `WINDBORNE.md` — WindBorne-specific system notes accumulated across sessions.
- `/start-session` reads all three before listing what's available. Completed chunks (have a notes file) are shown as DONE and skipped.

---

## Five learning tracks

| Track | Chunks |
|---|---|
| 1 — WindBorne architecture | 1.1 pipeline overview → 1.2 ingestion → 1.3 QC → 1.4 delivery → 1.5 Mission Control → 1.6 altitude API |
| 2 — ClickHouse + pipeline | 2.1 install + MergeTree → 2.2 queries → 2.3 TTL/partition → 2.4 hot-region schema → 2.5 ELT pipeline [needs 5.2] |
| 3 — MCP + agentic | 3.1 what MCP is → 3.2 build MCP server → 3.3 agentic dev → 3.4 monitoring agent [needs 2.5 + 5.3] |
| 4 — WeatherMesh | 4.1 NWP basics → 4.2 WeatherMesh 5c → 4.3 NetCDF → 4.4 toy model |
| 5 — Perf + reliability | 5.1 Protobuf [do before 2.5] → 5.2 observability [do before 3.4] → 5.3 resilience [needs 2.5] |
