import json

import pytest

from scheduler import create_backend


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
def test_policy_fixture_a(policy, expected):
    backend = create_backend(
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


def test_deadline_order_is_complete_expire_arrive_dispatch():
    backend = create_backend(
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


def test_metrics_and_linear_p95():
    backend = create_backend(initial_jobs=[job("A", 0, 2, 1, 10), job("B", 0, 4, 1, 10)])
    snapshot = backend.advance(6)
    assert snapshot["metrics"] == {
        "completed": 2,
        "expired": 0,
        "throughput": 20.0,
        "p95_latency": 5.8,
    }
    assert backend.advance(6)["metrics"]["throughput"] == 10.0


def test_policy_switch_does_not_preempt_running_job():
    backend = create_backend(
        initial_jobs=[job("A", 0, 5, 1, 20), job("B", 1, 4, 1, 20), job("C", 1, 1, 1, 20)]
    )
    backend.advance(1)
    backend.set_policy("sjf")
    assert backend.snapshot()["worker"]["job_id"] == "A"
    snapshot = backend.advance(4)
    assert snapshot["worker"]["job_id"] == "C"


def test_large_and_small_advance_match():
    jobs = [job("A", 0, 0.3, 1, 2), job("B", 0.3, 0.4, 2, 3)]
    large = create_backend(initial_jobs=jobs).advance(2)
    small_backend = create_backend(initial_jobs=jobs)
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


def test_validation_is_atomic_and_snapshot_is_defensive():
    backend = create_backend(initial_jobs=[])
    with pytest.raises(ValueError):
        backend.inject([job("A", 0, 1, 1, 2), job("A", 0, 1, 1, 2)])
    assert backend.snapshot()["jobs"] == []
    snapshot = backend.snapshot()
    snapshot["capacity"]["total"] = 99
    assert backend.snapshot()["capacity"]["total"] == 0


def test_capacity_and_invalid_values():
    backend = create_backend(initial_jobs=[])
    with pytest.raises(ValueError):
        backend.inject([job("A", 0, 1, 1, 2), job("B", 0, 0, 1, 2)])
    assert backend.snapshot()["capacity"]["total"] == 0
    with pytest.raises(ValueError):
        backend.advance(-1)
    with pytest.raises(ValueError):
        backend.generate(2)
    with pytest.raises(ValueError):
        backend.set_policy("hybrid")


def test_reset_reproducibility_and_json_serialization():
    first = create_backend().snapshot()
    second = create_backend().snapshot()
    assert first["jobs"] == second["jobs"]
    json.dumps(first)
    reset = create_backend().reset()
    assert reset["time"] == 0
    assert reset["policy"]["id"] == "fifo"
    assert [skill["id"] for skill in create_backend().list_skills()] == [
        "fifo",
        "sjf",
        "priority",
        "edf",
    ]


def test_pause_seam_freezes_simulation():
    backend = create_backend(initial_jobs=[job("A", 0, 2, 1, 5)])
    before = backend.snapshot()
    backend.pause_for_adaptation()
    with pytest.raises(RuntimeError):
        backend.advance(1)
    assert backend.snapshot()["time"] == before["time"]
    backend.resume_after_adaptation()
    assert backend.advance(1)["time"] == 1
