"""Safe local presentation of recorded Candidate evidence."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .lineage import Candidate


def present_candidate(candidate: Candidate) -> dict[str, Any]:
    """Return a defensive display record without trusting received evaluation data.

    A missing result is ``unchecked``. Any supplied result is ``unverified``:
    this disconnected component cannot validate a gate flag, Candidate status,
    sandbox provenance, or contract checks.
    """

    evidence_state = "unchecked" if candidate.evaluation_result is None else "unverified"
    return {
        "candidate_id": candidate.candidate_id,
        "parent_candidate_id": candidate.parent_candidate_id,
        "version": candidate.version,
        "reason": candidate.reason,
        "policy_code": candidate.policy_code,
        "workload_scope": deepcopy(candidate.workload_scope),
        "status": candidate.status,
        "status_evidence_state": "reported_unverified",
        "critic_feedback": deepcopy(candidate.critic_feedback),
        "evaluation_result": deepcopy(candidate.evaluation_result),
        "evaluation_evidence_state": evidence_state,
    }
