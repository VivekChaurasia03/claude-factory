# LEARN — General Concepts

Concepts that apply beyond WindBorne. Kafka, ClickHouse, Protobuf, etc.

---

## Kafka

### What it is
A durable, ordered log. Producers write messages to a topic. Consumers read at their own pace using an offset (a cursor into the log). Messages are retained for a configurable window (e.g., 7 days) regardless of whether they've been consumed.

### Offset replay
Reset a consumer's offset backward to reprocess old messages. Use case: bug in processing logic — fix it, replay, rewrite outputs with corrected data.

**Risk of naive replay:**
- Duplicate writes to downstream stores if those stores aren't idempotent
- Overwriting outputs that downstream systems already consumed (they won't automatically re-read)

### Consumer lag
Difference between the latest message in the topic and the consumer's current position. If lag grows, the consumer is falling behind — downstream systems get stale data. Lag = 0 after a consume run is the health signal.

### Manual vs auto offset commit
- `enable_auto_commit=True` (default): offset committed on a timer, before processing may finish. Crash between commit and write = silent data loss, no replay possible.
- `enable_auto_commit=False`: call `consumer.commit()` explicitly after processing. Crash before commit = message replayed on restart. This is at-least-once delivery.

### At-least-once delivery
Guarantee that every message is processed at least once. Implies duplicates are possible (crash after write, before commit → replay on restart). Downstream stores must be idempotent to handle this safely.

### Kafka UI (provectuslabs/kafka-ui)
Web dashboard for inspecting Kafka internals. Key views:
- **Topics** → Messages tab: see individual records with offset, partition, timestamp, value
- **Consumer Groups**: shows lag per partition — the operational health metric
- `__consumer_offsets` is Kafka's internal topic storing committed offset records. Read it via Consumer Groups tab, not directly.

---

## ClickHouse

### MergeTree engine
Columnar storage. Data is written in parts and merged in the background. Fast for analytics queries (reads a few columns across many rows). Slow if you insert row-by-row — always batch.

### ReplacingMergeTree
Variant that deduplicates rows with the same sort key during merges. Useful for idempotent replay — inserting the same record twice won't create duplicates (eventually, after merge runs).

---

## Protobuf

Binary serialization format. Schema-defined (`.proto` file). 5-10x smaller than equivalent JSON. No field names on the wire — uses field numbers instead. Fast to encode/decode.

Use when: wire cost matters (satellite, IoT), or serialization speed matters at high throughput.

---

## NetCDF

Multidimensional array format designed for scientific data. Supports variables (e.g., temperature as a 3D array: lat × lon × altitude) plus global metadata attributes. Standard input format for numerical weather models.

---

## Backfill jobs
A separate pipeline run over historical data to recompute or populate a store. Alternative to Kafka offset replay for longer time ranges or when the source data isn't in Kafka anymore.

