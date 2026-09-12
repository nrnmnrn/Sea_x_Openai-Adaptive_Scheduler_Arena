"""Internal Candidate lineage storage without planner or evaluator integration."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any


class CandidateLineageError(ValueError):
    """Raised when an internal Candidate lineage cannot be recorded."""


@dataclass(frozen=True)
class Candidate:
    """Internal carrier for backend-established Candidate field names.

    ``evaluation_result`` remains opaque received evidence. This is not a
    frozen shared schema or a promise of a public contract.
    """

    candidate_id: str
    parent_candidate_id: str | None
    version: int
    reason: str
    policy_code: str
    workload_scope: Any
    status: str
    critic_feedback: Any
    evaluation_result: Any


def _copied(candidate: Candidate) -> Candidate:
    """Canonicalize a record without invoking a Candidate subclass copy hook."""

    return Candidate(
        candidate_id=candidate.candidate_id,
        parent_candidate_id=candidate.parent_candidate_id,
        version=candidate.version,
        reason=candidate.reason,
        policy_code=candidate.policy_code,
        workload_scope=deepcopy(candidate.workload_scope),
        status=candidate.status,
        critic_feedback=deepcopy(candidate.critic_feedback),
        evaluation_result=deepcopy(candidate.evaluation_result),
    )


class CandidateLedger:
    """Maintain one bounded, linear Candidate chain for internal composition."""

    MAX_VERSIONS = 5

    def __init__(self) -> None:
        self._candidates: list[Candidate] = []

    def record(self, candidate: Candidate) -> Candidate:
        """Atomically add the next Candidate in the local lineage.

        This validates only lineage mechanics. It does not infer whether the
        candidate came from an all-failed result or whether evaluation passed.
        """

        self._validate_next(candidate)
        stored = _copied(candidate)
        returned = _copied(stored)
        self._candidates.append(stored)
        return returned

    def candidates(self) -> list[Candidate]:
        """Return defensive copies of the recorded Candidate chain."""

        return [_copied(candidate) for candidate in self._candidates]

    def get(self, candidate_id: str) -> Candidate:
        """Return a defensive copy of a recorded Candidate."""

        for candidate in self._candidates:
            if candidate.candidate_id == candidate_id:
                return _copied(candidate)
        raise KeyError(candidate_id)

    def _validate_next(self, candidate: Candidate) -> None:
        if not isinstance(candidate.candidate_id, str) or not candidate.candidate_id:
            raise CandidateLineageError("candidate_id must be a non-empty string")
        if any(item.candidate_id == candidate.candidate_id for item in self._candidates):
            raise CandidateLineageError("candidate_id must be unique")
        if isinstance(candidate.version, bool) or not isinstance(candidate.version, int):
            raise CandidateLineageError("version must be an integer")
        if candidate.version > self.MAX_VERSIONS:
            raise CandidateLineageError("a Candidate chain cannot exceed five versions")

        expected_version = len(self._candidates) + 1
        if candidate.version != expected_version:
            raise CandidateLineageError("version must be the next version in the Candidate chain")

        expected_parent = self._candidates[-1].candidate_id if self._candidates else None
        if candidate.parent_candidate_id != expected_parent:
            raise CandidateLineageError("parent_candidate_id must reference the previous version")
