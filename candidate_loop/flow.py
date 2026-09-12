"""Explicitly disconnected composition for the S03-A internal prototype."""

from __future__ import annotations

from typing import Any

from .lineage import Candidate, CandidateLedger
from .presentation import present_candidate


class DisconnectedRuntimeError(RuntimeError):
    """Raised when code attempts to run the unavailable external workflow."""


class DisconnectedCandidateFlow:
    """Compose local lineage and display without Planner or evaluator access."""

    def __init__(self, ledger: CandidateLedger | None = None) -> None:
        self._ledger = ledger or CandidateLedger()

    def record_candidate(self, candidate: Candidate) -> dict[str, Any]:
        """Record an internal Candidate and return its unverified display record."""

        return present_candidate(self._ledger.record(candidate))

    def present_candidate(self, candidate_id: str) -> dict[str, Any]:
        """Present an already-recorded Candidate without running evaluation."""

        return present_candidate(self._ledger.get(candidate_id))

    def run(self) -> None:
        """Refuse external execution until the upstream contracts are frozen."""

        raise DisconnectedRuntimeError(
            "Candidate runtime is disconnected: it cannot call a Planner or evaluator."
        )
