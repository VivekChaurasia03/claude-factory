import json
import time
import random
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from qc import QCChecker

TOPIC = "balloon-telemetry"
BROKERS = ["host.docker.internal:9092"]


# --- Simulates the HTTP ingestion endpoint ---
def produce_packets(n=20):
    producer = KafkaProducer(
        bootstrap_servers=BROKERS,
        value_serializer=lambda v: json.dumps(v).encode(),
        # In prod this would be Protobuf, not JSON
    )

    balloon_ids = ["wb-001", "wb-002", "wb-003"]
    seq = {b: 100 for b in balloon_ids}

    # Each balloon starts at a fixed position and drifts slightly each packet.
    # Real balloons move ~50-200 km/h — a 0.1° drift per 60s interval is ~11 km/h, plausible.
    positions = {
        "wb-001": {"lat": 37.4,  "lon": -122.0},
        "wb-002": {"lat": 51.5,  "lon":   -0.1},
        "wb-003": {"lat": -33.9, "lon":  151.2},
    }
    packet_interval_s = 60  # one packet per balloon per minute
    base_time = time.time()
    packet_count = {b: 0 for b in balloon_ids}

    for i in range(n):
        balloon_id = random.choice(balloon_ids)

        # Simulate occasional sequence gap (packet loss)
        if random.random() < 0.1:
            seq[balloon_id] += 2  # skip one
        else:
            seq[balloon_id] += 1

        # Advance position slightly — small realistic drift
        positions[balloon_id]["lat"] += round(random.uniform(-0.05, 0.05), 4)
        positions[balloon_id]["lon"] += round(random.uniform(-0.05, 0.05), 4)
        packet_count[balloon_id] += 1

        packet = {
            "balloon_id": balloon_id,
            "sequence_number": seq[balloon_id],
            "timestamp": base_time + packet_count[balloon_id] * packet_interval_s,
            "lat": round(positions[balloon_id]["lat"], 4),
            "lon": round(positions[balloon_id]["lon"], 4),
            "altitude": round(random.uniform(18000, 22000), 1),
            "pressure": round(random.uniform(50, 60), 2),
            "temp": round(random.uniform(-60, -40), 1),
        }

        # Partition by balloon_id — same balloon always hits same partition
        producer.send(TOPIC, value=packet, key=balloon_id.encode())
        print(f"  PRODUCED: {balloon_id} seq={seq[balloon_id]}")

    producer.flush()
    producer.close()
    print(f"\nProduced {n} packets.")


# --- Simulates Stage 3 consumer ---
def consume_packets():
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=BROKERS,
        group_id="stage3-qc-pipeline",
        auto_offset_reset="earliest",
        enable_auto_commit=False,          # manual commit only
        value_deserializer=lambda v: json.loads(v.decode()),
    )

    last_seq = {}  # track last sequence number per balloon
    # Single instance for the lifetime of the consumer — persistence and
    # spatial-temporal checks accumulate state across packets per balloon.
    checker = QCChecker()

    print("Consumer running. Ctrl+C to stop.\n")
    try:
        for message in consumer:
            packet = message.value
            balloon_id = packet["balloon_id"]
            seq = packet["sequence_number"]

            # Sequence gap detection
            if balloon_id in last_seq:
                expected = last_seq[balloon_id] + 1
                if seq != expected:
                    print(f"  !! GAP: {balloon_id} expected seq={expected}, got seq={seq} "
                        f"(lost {seq - expected} packet(s))")

            last_seq[balloon_id] = seq

            print(f"  CONSUMED: {balloon_id} seq={seq} "
                f"offset={message.offset} partition={message.partition}")

            # --- QC ---
            result = checker.check(packet)
            if result.passed:
                print(f"  QC PASS: {balloon_id}")
            else:
                print(f"  QC FAIL: {balloon_id} — {result.reasons}")

            # Commit AFTER processing — at-least-once guarantee
            consumer.commit()

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2 or sys.argv[1] == "produce":
        produce_packets()
    elif sys.argv[1] == "consume":
        consume_packets()