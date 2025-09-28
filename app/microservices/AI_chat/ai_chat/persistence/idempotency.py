"""Idempotency helper store for action executions.

Initial implementation: in-memory dictionary with TTL pruning executed lazily
on access. A future enhancement may replace this with Redis or a database
table for horizontal scaling / multi-process safety.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional
import time
import threading


@dataclass
class IdempotencyRecord:
    key: str
    created_at: float
    ttl_seconds: int
    value: Optional[dict] = None  # Optional associated metadata/result

    @property
    def is_expired(self) -> bool:
        return (time.time() - self.created_at) > self.ttl_seconds


class InMemoryIdempotencyStore:
    """A very small in-memory TTL store.

    Not process-safe for multi-worker deployments; acceptable for initial
    single-process dev use. Later we can plug a different backend by exposing
    the same interface (contains / store / get).
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._records: Dict[str, IdempotencyRecord] = {}

    def _prune_locked(self) -> None:
        expired = [k for k, v in self._records.items() if v.is_expired]
        for k in expired:
            self._records.pop(k, None)

    def store(self, key: str, ttl_seconds: int, value: Optional[dict] = None) -> bool:
        """Attempt to store a key.

        Returns False if key already exists and is still valid; True if stored.
        """
        with self._lock:
            self._prune_locked()
            rec = self._records.get(key)
            if rec and not rec.is_expired:
                return False
            self._records[key] = IdempotencyRecord(key=key, created_at=time.time(), ttl_seconds=ttl_seconds, value=value)
            return True

    def contains(self, key: str) -> bool:
        with self._lock:
            self._prune_locked()
            rec = self._records.get(key)
            return bool(rec and not rec.is_expired)

    def get(self, key: str) -> Optional[IdempotencyRecord]:
        with self._lock:
            self._prune_locked()
            rec = self._records.get(key)
            if rec and not rec.is_expired:
                return rec
            return None


# Singleton instance for easy import.
IDEMPOTENCY_STORE = InMemoryIdempotencyStore()

__all__ = [
    "IdempotencyRecord",
    "InMemoryIdempotencyStore",
    "IDEMPOTENCY_STORE",
]
