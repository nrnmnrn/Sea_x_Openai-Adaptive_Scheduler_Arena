import pytest

from candidate_loop.flow import DisconnectedCandidateFlow, DisconnectedRuntimeError
from candidate_loop.lineage import Candidate, CandidateLedger
from candidate_loop.presentation import present_candidate


def candidate(*, evaluation_result: object = None, status: str = "proposed") -> Candidate:
    return Candidate(
        candidate_id="c1",
        parent_candidate_id=None,
        version=1,
        reason="expired jobs increased",
        policy_code="return sorted(jobs)",
        workload_scope={"window": "w-1"},
        status=status,
        critic_feedback="try a deadline-aware ordering",
        evaluation_result=evaluation_result,
    )


def test_presentation_shows_candidate_code_reason_and_feedback() -> None:
    display = present_candidate(candidate())

    assert display["policy_code"] == "return sorted(jobs)"
    assert display["reason"] == "expired jobs increased"
    assert display["critic_feedback"] == "try a deadline-aware ordering"
    assert display["evaluation_evidence_state"] == "unchecked"
    assert display["status_evidence_state"] == "reported_unverified"


def test_supplied_passed_result_stays_visible_but_unverified() -> None:
    received = {"gate_passed": True, "sandbox_status": "passed"}
    display = present_candidate(candidate(evaluation_result=received, status="passed"))
    received["gate_passed"] = False
    display["evaluation_result"]["sandbox_status"] = "changed"

    assert display["evaluation_evidence_state"] == "unverified"
    assert display["evaluation_result"] == {"gate_passed": True, "sandbox_status": "changed"}
    assert received == {"gate_passed": False, "sandbox_status": "passed"}
    assert (
        present_candidate(candidate(evaluation_result={"gate_passed": True}))[
            "evaluation_evidence_state"
        ]
        == "unverified"
    )


def test_reported_passed_status_without_a_result_is_not_trusted() -> None:
    display = present_candidate(candidate(status="passed"))

    assert display["status"] == "passed"
    assert display["status_evidence_state"] == "reported_unverified"
    assert display["evaluation_evidence_state"] == "unchecked"


def test_disconnected_flow_only_records_and_presents_internal_candidates() -> None:
    flow = DisconnectedCandidateFlow(CandidateLedger())
    display = flow.record_candidate(candidate(evaluation_result={"gate_passed": True}))

    assert display["candidate_id"] == "c1"
    assert display["evaluation_evidence_state"] == "unverified"
    assert flow.present_candidate("c1")["policy_code"] == "return sorted(jobs)"


def test_disconnected_runtime_cannot_accept_upstream_truth_or_execute() -> None:
    flow = DisconnectedCandidateFlow()

    with pytest.raises(TypeError):
        flow.run(all_skills_failed=True)  # type: ignore[call-arg]
    with pytest.raises(DisconnectedRuntimeError, match="disconnected"):
        flow.run()
