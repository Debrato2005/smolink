# IDs combine elapsed milliseconds, a 10-bit worker ID, and a 12-bit sequence.
# Worker values are 0-1023. Sequence values are 0-4095 per millisecond.
# (1 << n) - 1 is the largest value representable by n bits.
# Subtracting a fixed epoch reduces the timestamp value before shifting.
# CUSTOM_EPOCH_MS equals 1970-07-27T02:24:16.123Z. Keep it stable after issuance.
# The intended 64-bit layout reserves 41 timestamp bits and one sign bit.
# The implementation does not enforce that timestamp bound.
# A lock coordinates threads using this instance, not independent generators.
# Assign distinct worker IDs or share sequence state across generators.
# A backward clock raises. Sequence overflow waits for the next millisecond.

import time
from threading import Lock


CUSTOM_EPOCH_MS = 17_893_456_123  # 1970-07-27T02:24:16.123Z
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
