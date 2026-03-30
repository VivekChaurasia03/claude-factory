import math
import time
from dataclasses import dataclass, field
from collections import defaultdict

# --- Constants ---

PLAUSIBILITY_BOUNDS = {
    "altitude": (-500, 40_000),    # meters
    "temp":     (-100, 60),        # °C
    "humidity": (0, 100),          # %
    "pressure": (1, 1100),         # hPa
}

PERSISTENCE_WINDOW   = 5      # flag if same value for this many consecutive packets
PERSISTENCE_FIELDS   = ("temp", "humidity")

MAX_BALLOON_SPEED_KMH = 300   # anything faster = teleport, not flight
RELATIONAL_TOLERANCE  = 0.20  # ±20% on barometric altitude estimate


# --- Result type ---

@dataclass
class QCResult:
    passed: bool
    checks: dict = field(default_factory=dict)   # {"plausibility": True, ...}
    reasons: list = field(default_factory=list)  # human-readable failure reasons


# --- QC logic ---

def _check_plausibility(packet: dict) -> tuple[bool, list[str]]:
    reasons = []
    for field_name, (lo, hi) in PLAUSIBILITY_BOUNDS.items():
        if field_name not in packet:
            continue
        val = packet[field_name]
        if not (lo <= val <= hi):
            reasons.append(f"plausibility: {field_name}={val} outside [{lo}, {hi}]")
    return len(reasons) == 0, reasons


def _check_relational(packet: dict) -> tuple[bool, list[str]]:
    # Barometric formula: given pressure, estimate what altitude should be.
    # If the GPS altitude disagrees by >20%, the sensors are contradicting each other.
    pressure = packet.get("pressure")
    altitude = packet.get("altitude")
    if pressure is None or altitude is None:
        return True, []

    estimated_altitude = 44_330 * (1 - (pressure / 1013.25) ** 0.1903)
    if estimated_altitude == 0:
        return True, []

    error = abs(altitude - estimated_altitude) / abs(estimated_altitude)
    if error > RELATIONAL_TOLERANCE:
        reason = (
            f"relational: altitude={altitude}m but pressure={pressure}hPa "
            f"implies ~{estimated_altitude:.0f}m (error={error:.0%})"
        )
        return False, [reason]

    return True, []


class QCChecker:
    """
    Stateful QC checker — must be a single instance per consumer process.

    Persistence and spatial-temporal checks require memory of previous packets
    per balloon. Keeping that state here means the consumer loop stays clean:
    it just calls checker.check(packet) and gets a result back.
    """

    def __init__(self):
        # Per-balloon ring buffer of recent values for persistence detection.
        # Key: balloon_id. Value: dict of field -> list of last N values.
        self._persistence_history: dict[str, dict[str, list]] = defaultdict(
            lambda: defaultdict(list)
        )

        # Per-balloon last known position + timestamp for speed calculation.
        # Key: balloon_id. Value: (lat, lon, timestamp).
        self._last_position: dict[str, tuple[float, float, float]] = {}

    def check(self, packet: dict) -> QCResult:
        checks = {}
        all_reasons = []

        ok, reasons = _check_plausibility(packet)
        checks["plausibility"] = ok
        all_reasons.extend(reasons)

        ok, reasons = _check_relational(packet)
        checks["relational"] = ok
        all_reasons.extend(reasons)

        ok, reasons = self._check_persistence(packet)
        checks["persistence"] = ok
        all_reasons.extend(reasons)

        ok, reasons = self._check_spatial_temporal(packet)
        checks["spatial_temporal"] = ok
        all_reasons.extend(reasons)

        return QCResult(
            passed=all(checks.values()),
            checks=checks,
            reasons=all_reasons,
        )

    def _check_persistence(self, packet: dict) -> tuple[bool, list[str]]:
        balloon_id = packet["balloon_id"]
        history = self._persistence_history[balloon_id]
        reasons = []

        for f in PERSISTENCE_FIELDS:
            if f not in packet:
                continue
            val = round(packet[f], 2)

            history[f].append(val)
            # Only keep the last N values — we don't need older ones
            if len(history[f]) > PERSISTENCE_WINDOW:
                history[f].pop(0)

            # Flag if every value in the window is identical
            if len(history[f]) == PERSISTENCE_WINDOW and len(set(history[f])) == 1:
                reasons.append(
                    f"persistence: {f} stuck at {val} "
                    f"for {PERSISTENCE_WINDOW} consecutive packets"
                )

        return len(reasons) == 0, reasons

    def _check_spatial_temporal(self, packet: dict) -> tuple[bool, list[str]]:
        balloon_id = packet["balloon_id"]
        lat = packet.get("lat")
        lon = packet.get("lon")
        ts  = packet.get("timestamp")

        if lat is None or lon is None or ts is None:
            return True, []

        if balloon_id not in self._last_position:
            self._last_position[balloon_id] = (lat, lon, ts)
            return True, []

        prev_lat, prev_lon, prev_ts = self._last_position[balloon_id]
        self._last_position[balloon_id] = (lat, lon, ts)

        elapsed_hours = (ts - prev_ts) / 3600
        if elapsed_hours <= 0:
            return True, []

        distance_km = _haversine_km(prev_lat, prev_lon, lat, lon)
        speed_kmh = distance_km / elapsed_hours

        if speed_kmh > MAX_BALLOON_SPEED_KMH:
            reason = (
                f"spatial_temporal: {balloon_id} moved {distance_km:.1f}km "
                f"in {elapsed_hours * 60:.1f}min ({speed_kmh:.0f} km/h > {MAX_BALLOON_SPEED_KMH})"
            )
            return False, [reason]

        return True, []


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    # Standard haversine — great-circle distance between two lat/lon points.
    R = 6371  # Earth radius in km
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )
    return R * 2 * math.asin(math.sqrt(a))


# --- Test runner ---

if __name__ == "__main__":
    checker = QCChecker()
    now = time.time()

    test_packets = [
        # PASS — normal stratospheric balloon
        {
            "balloon_id": "wb-001", "timestamp": now,
            "lat": 37.4, "lon": -122.0,
            "altitude": 20_000, "pressure": 55.0, "temp": -55.0, "humidity": 10.0,
        },
        # FAIL plausibility — altitude below sea floor
        {
            "balloon_id": "wb-002", "timestamp": now,
            "lat": 40.0, "lon": -100.0,
            "altitude": -800, "pressure": 55.0, "temp": -50.0, "humidity": 12.0,
        },
        # FAIL relational — pressure says sea level, altitude says stratosphere
        {
            "balloon_id": "wb-003", "timestamp": now,
            "lat": 35.0, "lon": -90.0,
            "altitude": 20_000, "pressure": 950.0, "temp": -52.0, "humidity": 8.0,
        },
        # FAIL persistence — humidity stuck at 42.0 five times in a row
        *[
            {
                "balloon_id": "wb-004", "timestamp": now + i,
                "lat": 50.0, "lon": 10.0,
                "altitude": 19_500, "pressure": 57.0, "temp": -58.0, "humidity": 42.0,
            }
            for i in range(5)
        ],
        # FAIL spatial_temporal — teleported ~8000 km in 1 second
        {
            "balloon_id": "wb-005", "timestamp": now,
            "lat": 0.0, "lon": 0.0,
            "altitude": 20_000, "pressure": 55.0, "temp": -50.0, "humidity": 10.0,
        },
        {
            "balloon_id": "wb-005", "timestamp": now + 1,
            "lat": 70.0, "lon": 100.0,
            "altitude": 20_000, "pressure": 55.0, "temp": -50.0, "humidity": 10.0,
        },
    ]

    for packet in test_packets:
        result = checker.check(packet)
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {packet['balloon_id']}")
        for reason in result.reasons:
            print(f"       {reason}")
