import pytest

from candidate_loop.lineage import Candidate, CandidateLedger, CandidateLineageError


class CopyFailure:
    def __deepcopy__(self, memo: object) -> object:
        raise RuntimeError("cannot copy")


class DuplicateCopyCandidate(Candidate):
    def __deepcopy__(self, memo: object) -> Candidate:
        return candidate("c1", 1)


def candidate(
    candidate_id: str,
    version: int,
    parent_candidate_id: str | None = None,
    **overrides: object,
) -> Candidate:
    values: dict[str, object] = {
        "candidate_id": candidate_id,
        "parent_candidate_id": parent_candidate_id,
        "version": version,
        "reason": "workload degradation",
        "policy_code": "return jobs",
        "workload_scope": {"window": "w-1"},
        "status": "proposed",
        "critic_feedback": None,
        "evaluation_result": None,
    }
    values.update(overrides)
    return Candidate(**values)  # type: ignore[arg-type]


def test_records_a_bounded_linear_candidate_chain() -> None:
    ledger = CandidateLedger()
    first = ledger.record(candidate("c1", 1))
    second = ledger.record(candidate("c2", 2, first.candidate_id))

    assert [item.candidate_id for item in ledger.candidates()] == ["c1", "c2"]
    assert second.parent_candidate_id == "c1"


@pytest.mark.parametrize(
    "invalid",
    [
        candidate("c1", True),
        candidate("c1", 2),
        candidate("c1", 1, "missing-parent"),
    ],
)
def test_rejects_invalid_initial_candidate_without_recording(invalid: Candidate) -> None:
    ledger = CandidateLedger()

    with pytest.raises(CandidateLineageError):
        ledger.record(invalid)

    assert ledger.candidates() == []


def test_rejects_duplicate_id_and_wrong_parent_atomically() -> None:
    ledger = CandidateLedger()
    ledger.record(candidate("c1", 1))

    with pytest.raises(CandidateLineageError):
        ledger.record(candidate("c1", 2, "c1"))
    with pytest.raises(CandidateLineageError):
        ledger.record(candidate("c2", 2, "wrong"))

    assert [item.candidate_id for item in ledger.candidates()] == ["c1"]


def test_copy_failure_does_not_append_a_partial_candidate() -> None:
    ledger = CandidateLedger()
    ledger.record(candidate("c1", 1))

    with pytest.raises(RuntimeError, match="cannot copy"):
        ledger.record(candidate("c2", 2, "c1", workload_scope=CopyFailure()))

    assert [item.candidate_id for item in ledger.candidates()] == ["c1"]


def test_subclass_copy_hook_cannot_replace_validated_lineage() -> None:
    ledger = CandidateLedger()
    ledger.record(candidate("c1", 1))
    supplied = DuplicateCopyCandidate(
        candidate_id="c2",
        parent_candidate_id="c1",
        version=2,
        reason="workload degradation",
        policy_code="return jobs",
        workload_scope={"window": "w-1"},
        status="proposed",
        critic_feedback=None,
        evaluation_result=None,
    )

    recorded = ledger.record(supplied)

    assert type(recorded) is Candidate
    assert [(item.candidate_id, item.version) for item in ledger.candidates()] == [
        ("c1", 1),
        ("c2", 2),
    ]


def test_fifth_candidate_is_allowed_and_sixth_is_rejected_atomically() -> None:
    ledger = CandidateLedger()
    parent = None
    for version in range(1, 6):
        current = ledger.record(candidate(f"c{version}", version, parent))
        parent = current.candidate_id

    with pytest.raises(CandidateLineageError, match="five versions"):
        ledger.record(candidate("c6", 6, "c5"))

    assert [item.version for item in ledger.candidates()] == [1, 2, 3, 4, 5]


def test_ledger_keeps_and_returns_defensive_copies() -> None:
    ledger = CandidateLedger()
    scope = {"jobs": ["j1"]}
    stored = ledger.record(candidate("c1", 1, workload_scope=scope))
    scope["jobs"].append("j2")
    stored.workload_scope["jobs"].append("j3")

    retrieved = ledger.get("c1")
    retrieved.workload_scope["jobs"].append("j4")

    assert ledger.get("c1").workload_scope == {"jobs": ["j1"]}
