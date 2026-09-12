import json

import pytest

from scheduler import AdapterOperationError


def job(job_id, arrival, processing_time, priority, deadline):
    return {
        "id": job_id,
        "arrival": arrival,
        "processing_time": processing_time,
        "priority": priority,
        "deadline": deadline,
    }


@pytest.mark.parametrize(
    "policy, expected", [("fifo", "A"), ("sjf", "B"), ("priority", "C"), ("edf", "D")]
)
def test_policy_fixture_a(policy, expected, backend_factory):
    backend = backend_factory(
        initial_jobs=[
            job("A", 1, 6, 2, 25),
            job("B", 1, 2, 1, 12),
            job("C", 1, 4, 5, 18),
            job("D", 1, 3, 3, 9),
        ]
    )
    backend.set_policy(policy)
    snapshot = backend.advance(1)
    assert snapshot["worker"]["job_id"] == expected


def test_deadline_order_is_complete_expire_arrive_dispatch(backend_factory):
    backend = backend_factory(
        initial_jobs=[
            job("A", 0, 2, 1, 2),
            job("B", 0, 3, 1, 2),
            job("C", 2, 1, 1, 4),
        ]
    )
    snapshot = backend.advance(2)
    assert [event["type"] for event in snapshot["events"][-4:]] == [
        "completed",
        "expired",
        "arrived",
        "started",
    ]
    assert snapshot["worker"]["job_id"] == "C"
    assert next(item for item in snapshot["jobs"] if item["id"] == "B")["status"] == "expired"


def test_metrics_and_linear_p95(backend_factory):
    backend = backend_factory(initial_jobs=[job("A", 0, 2, 1, 10), job("B", 0, 4, 1, 10)])
    snapshot = backend.advance(6)
    assert snapshot["metrics"] == {
        "completed": 2,
        "expired": 0,
        "throughput": 20.0,
        "p95_latency": 5.8,
    }
    assert backend.advance(6)["metrics"]["throughput"] == 10.0


def test_policy_switch_does_not_preempt_running_job(backend_factory):
    backend = backend_factory(
        initial_jobs=[job("A", 0, 5, 1, 20), job("B", 1, 4, 1, 20), job("C", 1, 1, 1, 20)]
    )
    backend.advance(1)
    backend.set_policy("sjf")
    assert backend.snapshot()["worker"]["job_id"] == "A"
    snapshot = backend.advance(4)
    assert snapshot["worker"]["job_id"] == "C"


def test_large_and_small_advance_match(backend_factory):
    jobs = [job("A", 0, 0.3, 1, 2), job("B", 0.3, 0.4, 2, 3)]
    large = backend_factory(initial_jobs=jobs).advance(2)
    small_backend = backend_factory(initial_jobs=jobs)
    for _ in range(20):
        small_backend.advance(0.1)
    small = small_backend.snapshot()
    assert [(item["id"], item["status"], item["completed_at"]) for item in large["jobs"]] == [
        (item["id"], item["status"], item["completed_at"]) for item in small["jobs"]
    ]
    assert large["metrics"] == small["metrics"]
    assert [(event["type"], event["job_id"]) for event in large["events"]] == [
        (event["type"], event["job_id"]) for event in small["events"]
    ]


def test_validation_is_atomic_and_snapshot_is_defensive(backend_factory):
    backend = backend_factory(initial_jobs=[])
    with pytest.raises(ValueError):
        backend.inject([job("A", 0, 1, 1, 2), job("A", 0, 1, 1, 2)])
    assert backend.snapshot()["jobs"] == []
    snapshot = backend.snapshot()
    snapshot["capacity"]["total"] = 99
    assert backend.snapshot()["capacity"]["total"] == 0


def test_capacity_and_invalid_values(backend_factory):
    backend = backend_factory(initial_jobs=[])
    with pytest.raises(ValueError):
        backend.inject([job("A", 0, 1, 1, 2), job("B", 0, 0, 1, 2)])
    assert backend.snapshot()["capacity"]["total"] == 0
    with pytest.raises(ValueError):
        backend.advance(-1)
    with pytest.raises(ValueError):
        backend.generate(2)
    with pytest.raises(ValueError):
        backend.set_policy("hybrid")


def test_reset_reproducibility_and_json_serialization(backend_factory):
    first = backend_factory().snapshot()
    second = backend_factory().snapshot()
    assert first["jobs"] == second["jobs"]
    json.dumps(first)
    reset = backend_factory().reset()
    assert reset["time"] == 0
    assert reset["policy"]["id"] == "fifo"
    assert [skill["id"] for skill in backend_factory().list_skills()] == [
        "fifo",
        "sjf",
        "priority",
        "edf",
    ]


def test_reset_changes_run_identity_without_changing_seeded_workload(backend_factory):
    backend = backend_factory()
    before = backend.snapshot()
    after = backend.reset()
    assert after["run_id"] != before["run_id"]
    assert after["jobs"] == before["jobs"]


def test_expired_job_is_attributed_to_active_segment(backend_factory):
    backend = backend_factory(initial_jobs=[job("A", 0, 3, 1, 2)])
    snapshot = backend.advance(2)
    expired = next(item for item in snapshot["jobs"] if item["id"] == "A")
    assert expired["status"] == "expired"
    assert expired["dispatched_policy_id"] is None
    assert expired["segment_id"] == snapshot["segments"][-1]["id"]


def test_pause_seam_freezes_simulation(backend_factory):
    backend = backend_factory(initial_jobs=[job("A", 0, 2, 1, 5)])
    before = backend.snapshot()
    backend.pause_for_adaptation()
    with pytest.raises(RuntimeError):
        backend.advance(1)
    assert backend.snapshot()["time"] == before["time"]
    backend.resume_after_adaptation()
    assert backend.advance(1)["time"] == 1


def test_snapshot_adaptation_includes_neutral_workload_window(backend_factory):
    assert "workload_window" in backend_factory().snapshot()["adaptation"]
    assert backend_factory().snapshot()["adaptation"]["workload_window"] is None


def test_expiry_trigger_stops_at_first_five_second_boundary_and_rejects_mutations(backend_factory):
    backend = backend_factory(initial_jobs=[job("A", 0, 10, 1, 2), job("B", 0, 1, 1, 20)])
    snapshot = backend.advance(12)
    adaptation = snapshot["adaptation"]
    assert snapshot["time"] == 5
    assert adaptation["workload_window"] == {"id": "window-0-5", "start": 0.0, "end": 5.0}
    assert adaptation["context_id"] == f"{snapshot['run_id']}:{snapshot['snapshot_version']}"
    for operation in (
        lambda: backend.advance(1),
        lambda: backend.inject([job("C", 5, 1, 1, 10)]),
        lambda: backend.generate(1),
        lambda: backend.set_policy("sjf"),
    ):
        with pytest.raises(AdapterOperationError):
            operation()
    assert backend.snapshot()["time"] == 5


def test_reset_invalidates_old_adaptation_context(backend_factory):
    backend = backend_factory(initial_jobs=[job("A", 0, 10, 1, 2)])
    context_id = backend.advance(5)["adaptation"]["context_id"]
    backend.reset()
    with pytest.raises(ValueError):
        backend.clone_for_evaluation(context_id)
    with pytest.raises(ValueError):
        backend.record_existing_evaluation(context_id, "incomplete")


def test_generate_skips_existing_job_ids(backend_factory):
    backend = backend_factory(initial_jobs=[job("J2", 0, 1, 1, 5)])
    snapshot = backend.generate(1)
    assert {item["id"] for item in snapshot["jobs"]} == {"J1", "J2"}


def test_paused_advance_zero_is_rejected_without_version_change(backend_factory):
    backend = backend_factory()
    backend.pause_for_adaptation()
    before = backend.snapshot()
    with pytest.raises(AdapterOperationError):
        backend.advance(0)
    after = backend.snapshot()
    assert after["snapshot_version"] == before["snapshot_version"]
    assert after["time"] == before["time"]


def test_time_boundaries_do_not_use_tolerance(backend_factory):
    arrival = 1.0000000005
    backend = backend_factory(initial_jobs=[job("A", arrival, 1, 1, 4)])
    snapshot = backend.advance(1)
    assert next(item for item in snapshot["jobs"] if item["id"] == "A")["status"] == "scheduled"

    backend = backend_factory(initial_jobs=[job("A", 0, 1.0000000005, 1, 1.000000001)])
    snapshot = backend.advance(1)
    assert next(item for item in snapshot["jobs"] if item["id"] == "A")["status"] == "running"

    backend = backend_factory(initial_jobs=[job("A", 0, 1.0000000005, 1, 1)])
    snapshot = backend.advance(1)
    assert next(item for item in snapshot["jobs"] if item["id"] == "A")["status"] == "expired"
