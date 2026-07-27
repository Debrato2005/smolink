import time
from threading import Lock


CUSTOM_EPOCH_MS = 17_893_456_123 # Jan 1, 2026 00:00:00 UTC
WORKER_ID_BITS = 10
SEQUENCE_BITS = 12
MAX_WORKER_ID = (1 << WORKER_ID_BITS) - 1
MAX_SEQUENCE = (1 << SEQUENCE_BITS) - 1


class SnowflakeGenerator:
    def __init__(self, worker_id: int) -> None:
        if not 0 <= worker_id <= MAX_WORKER_ID:
            raise ValueError(f"worker_id must be between 0 and {MAX_WORKER_ID}")

        self._worker_id = worker_id
        self._sequence = 0
        self._last_timestamp = -1
        self._lock = Lock()

    def next_id(self) -> int:
        with self._lock:
            timestamp = self._current_timestamp()

            if timestamp < self._last_timestamp:
                raise RuntimeError("System clock moved backwards")

            if timestamp == self._last_timestamp:
                self._sequence = (self._sequence + 1) & MAX_SEQUENCE

                if self._sequence == 0:
                    timestamp = self._wait_for_next_millisecond()
            else:
                self._sequence = 0

            self._last_timestamp = timestamp

            return (
                ((timestamp - CUSTOM_EPOCH_MS) << (WORKER_ID_BITS + SEQUENCE_BITS))
                | (self._worker_id << SEQUENCE_BITS)
                | self._sequence
            )

    def _current_timestamp(self) -> int:
        return time.time_ns() // 1_000_000

    def _wait_for_next_millisecond(self) -> int:
        timestamp = self._current_timestamp()

        while timestamp <= self._last_timestamp:
            timestamp = self._current_timestamp()

        return timestamp


# =============================================================================
# Snowflake ID Generator
#
# Generates globally unique, time-ordered 64-bit integer IDs without requiring
# a central database.
#
# ID Layout (64 bits)
#
#   0 |--------- Timestamp ---------|-- Worker ID --|-- Sequence --|
#     |          41 bits            |    10 bits    |    12 bits    |
#
# Components
# ----------
# • Timestamp : Milliseconds since the custom epoch (Jan 1, 2026 UTC).
# • Worker ID : Identifies the machine/service generating the ID.
# • Sequence  : Counter (0-4095) allowing multiple IDs in the same millisecond.
#
# Why a Custom Epoch?
# -------------------
# The operating system measures time as milliseconds since the Unix epoch
# (Jan 1, 1970 UTC). Snowflake subtracts a fixed custom epoch so timestamps
# start near zero for this application, reducing wasted timestamp space.
#
#     snowflake_timestamp = current_unix_time_ms - CUSTOM_EPOCH_MS
#
# The custom epoch is chosen once and MUST NEVER change after IDs have been
# generated, otherwise old and new IDs become incompatible.
#
# Bit Allocation
# --------------
# WORKER_ID_BITS = 10  -> 2^10 = 1024 workers (IDs 0-1023)
# SEQUENCE_BITS  = 12  -> 2^12 = 4096 IDs per worker per millisecond
#
# Why (1 << n) - 1?
# -----------------
# Left shifting 1 by n bits computes 2^n.
#
#     1 << n == 2^n
#
# This is the first value that requires (n + 1) bits. Subtracting one fills
# the lower n bits with 1s, producing the largest value representable in n bits.
#
# Example:
#
#     1 << 10      -> 10000000000₂ = 1024
#     (1 << 10)-1  -> 01111111111₂ = 1023
#
# Hence:
#
#     MAX_WORKER_ID = (1 << WORKER_ID_BITS) - 1
#     MAX_SEQUENCE  = (1 << SEQUENCE_BITS) - 1
#
# Thread Safety
# -------------
# A mutex (Lock) ensures only one thread generates an ID at a time, preventing
# duplicate sequence values under concurrent access.
#
# Clock Handling
# --------------
# • If the clock moves backwards, generation stops with an exception.
# • If the sequence overflows within the same millisecond, the generator waits
#   until the next millisecond before producing another ID.
# =============================================================================