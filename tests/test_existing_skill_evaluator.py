import pytest

from existing_skill_adaptation import (
    ExistingSkillComparisonOutcome,
    classify_existing_skill_comparison,
)
from existing_skill_evaluator import _trace_errors, evaluate_builtin_existing_skills
from scheduler import AdapterValidationError


def _job(job_id, arrival, processing_time, priority, deadline):
    return {
        "id": job_id,
        "arrival": arrival,
        "processing_time": processing_time,
        "priority": priority,
        "deadline": deadline,
    }


def _trigger(run_id):
    return {
        "triggered": True,
        "reason": "expired jobs increased",
        "run_id": run_id,
        "workload_window": {"id": "window-1", "start": 0, "end": 1},
        "adaptation_id": "adaptation-1",
    }


def test_replay_uses_nonzero_checkpoint_and_does_not_mutate_live(backend_factory):
    backend = backend_factory(
        initial_jobs=[
            _job("A", 0, 4, 1, 20),
            _job("B", 1, 1, 5, 8),
            _job("C", 1, 2, 1, 12),
        ]
    )
    backend.advance(1)
    backend.pause_for_adaptation()
    before = backend.snapshot()

    context_id = f"{before['run_id']}:{before['snapshot_version']}"
    comparison = evaluate_builtin_existing_skills(backend, _trigger(before["run_id"]), context_id)

    assert comparison.run_id == before["run_id"]
    assert comparison.context_id == context_id
    assert comparison.evaluation_window["start"] == before["time"]
    assert comparison.evaluation_window != _trigger(before["run_id"])["workload_window"]
    assert {item["subject_id"] for item in comparison.evaluations} == {
        "fifo",
        "sjf",
        "priority",
        "edf",
    }
    assert backend.snapshot() == before
    assert classify_existing_skill_comparison(comparison) in {
        ExistingSkillComparisonOutcome.PASS,
        ExistingSkillComparisonOutcome.ALL_FAILED,
    }


def test_replay_rejects_an_unbound_context_id(backend_factory):
    backend = backend_factory(initial_jobs=[_job("A", 0, 1, 1, 5)])

    with pytest.raises(AdapterValidationError, match="context_id"):
        evaluate_builtin_existing_skills(backend, _trigger(backend.run_id), "different")


def test_trace_rejects_overlapping_or_preempted_dispatches():
    snapshot = {
        "events": [
            {"seq": 1, "time": 0, "type": "started", "job_id": "A"},
            {"seq": 2, "time": 1, "type": "started", "job_id": "B"},
        ],
        "jobs": [
            {
                "id": "A",
                "status": "completed",
                "started_at": 0,
                "completed_at": 2,
                "processing_time": 3,
                "deadline": 5,
            },
            {"id": "B", "status": "running", "started_at": 1, "processing_time": 2, "deadline": 5},
        ],
    }

    assert _trace_errors(snapshot, {"A", "B"})
