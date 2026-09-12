"""Replay built-in verified Skills from one isolated scheduler checkpoint."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from typing import Any

from existing_skill_adaptation import (
    ExistingSkillComparison,
    ExistingSkillComparisonAssembler,
    evaluate_existing_skill_gate,
)
from scheduler import INITIAL_SKILLS, SchedulerBackend, _p95


class ExistingSkillEvaluationIncompleteError(RuntimeError):
    """A replay cannot provide complete evidence and must not start Planner."""


def _score(
    backend: SchedulerBackend, job_ids: set[str], start: float, end: float
) -> dict[str, int | float | None]:
    jobs = [job for job in backend.snapshot()["jobs"] if job["id"] in job_ids]
    completed = [job for job in jobs if job["status"] == "completed"]
    return {
        "completed": len(completed),
        "expired": sum(job["status"] == "expired" for job in jobs),
        "p95_latency": _p95([job["completed_at"] - job["arrival"] for job in completed]),
        "throughput": len(completed) / (end - start) * 60 if end > start else None,
    }


def _trace_errors(snapshot: Mapping[str, Any], job_ids: set[str]) -> list[str]:
    errors = []
    jobs = [job for job in snapshot["jobs"] if job["id"] in job_ids]
    intervals = []
    starts = {event["job_id"]: event for event in snapshot["events"] if event["type"] == "started"}
    for job in jobs:
        if job["status"] == "completed":
            expected_end = job["started_at"] + job["processing_time"]
            if not math.isclose(job["completed_at"], expected_end):
                errors.append(f"{job['id']} duration is preempted or inconsistent")
            if job["completed_at"] > job["deadline"]:
                errors.append(f"{job['id']} completed after its deadline")
            intervals.append((job["started_at"], job["completed_at"], job["id"]))
        if job["status"] == "running":
            intervals.append(
                (job["started_at"], job["started_at"] + job["processing_time"], job["id"])
            )
        if job["status"] in {"completed", "running"} and job["id"] not in starts:
            errors.append(f"{job['id']} has no dispatch event")
    for (_, end, prior), (start, _, current) in zip(sorted(intervals), sorted(intervals)[1:]):
        if start < end:
            errors.append(f"{prior} overlaps {current}")
    event_order = {"completed": 0, "expired": 1, "arrived": 2, "started": 3}
    for left, right in zip(snapshot["events"], snapshot["events"][1:]):
        if left["time"] == right["time"] and event_order.get(left["type"], 4) > event_order.get(
            right["type"], 4
        ):
            errors.append("same-time event order is invalid")
    return errors


def _run_policy(
    checkpoint: SchedulerBackend,
    context_id: str,
    policy_id: str,
    job_ids: set[str],
    until: float,
) -> tuple[dict[str, int | float | None], tuple[str, ...]]:
    try:
        replay = checkpoint.clone_for_evaluation(context_id)
        replay.set_policy(policy_id, reason="evaluation replay")
        replay.advance(max(0.0, until - replay.time))
    except Exception as error:
        raise ExistingSkillEvaluationIncompleteError(
            f"{policy_id} replay could not complete: {error}"
        ) from error
    snapshot = replay.snapshot()
    errors = _trace_errors(snapshot, job_ids)
    if [event["seq"] for event in snapshot["events"]] != list(
        range(1, len(snapshot["events"]) + 1)
    ):
        errors.append("event sequence is not contiguous")
    if any(event["time"] > snapshot["time"] for event in snapshot["events"]):
        errors.append("event time exceeds replay time")
    for job in snapshot["jobs"]:
        if job["id"] in job_ids:
            if job["status"] not in {"completed", "expired"}:
                errors.append(f"{job['id']} did not reach a terminal state")
            if not all(
                math.isfinite(job[field]) for field in ("arrival", "processing_time", "deadline")
            ):
                errors.append(f"{job['id']} has non-finite scheduling data")
    try:
        json.dumps(snapshot)
    except (TypeError, ValueError):
        errors.append("snapshot is not JSON serializable")
    if errors:
        raise ExistingSkillEvaluationIncompleteError("; ".join(errors))
    return _score(replay, job_ids, checkpoint.time, until), tuple(errors)


def evaluate_builtin_existing_skills(
    backend: SchedulerBackend,
    trigger: Mapping[str, Any],
    context_id: str,
    assembler: ExistingSkillComparisonAssembler | None = None,
) -> ExistingSkillComparison:
    """Evaluate FIFO and every verified built-in Skill without mutating live state."""

    checkpoint = backend.clone_for_evaluation(context_id)
    if trigger.get("run_id") != checkpoint.run_id:
        raise ValueError("TriggerResult run_id does not match the evaluation checkpoint")
    observation_window = trigger.get("workload_window")
    if (
        not isinstance(observation_window, Mapping)
        or observation_window.get("end") != checkpoint.time
    ):
        raise ValueError("TriggerResult workload_window must end at the evaluation checkpoint")
    remaining = {
        job.id for job in checkpoint.jobs.values() if job.status not in {"completed", "expired"}
    }
    if not remaining:
        raise ValueError("evaluation requires at least one non-terminal Job")
    until = max(checkpoint.jobs[job_id].deadline for job_id in remaining)
    evaluation_window = {"id": f"{context_id}:evaluation", "start": checkpoint.time, "end": until}
    skills = [skill for skill in checkpoint.list_skills() if skill["verified"]]
    verified = [skill["id"] for skill in skills]
    if any(skill_id not in INITIAL_SKILLS for skill_id in verified):
        raise ValueError("built-in replay only supports verified built-in Skills")

    baseline, baseline_errors = _run_policy(checkpoint, context_id, "fifo", remaining, until)
    if baseline_errors:
        raise ExistingSkillEvaluationIncompleteError("; ".join(baseline_errors))
    evaluations = []
    for skill_id in verified:
        metrics, trace_errors = _run_policy(checkpoint, context_id, skill_id, remaining, until)
        contract_validation = not trace_errors
        gate_passed = evaluate_existing_skill_gate(baseline, metrics, contract_validation, "passed")
        evaluations.append(
            {
                "subject_id": skill_id,
                "subject_kind": "skill",
                "baseline_metrics": baseline,
                "evaluated_metrics": metrics,
                "evaluation_window": evaluation_window,
                "gate_passed": gate_passed,
                "regressions": list(trace_errors),
                "contract_validation": contract_validation,
                "sandbox_status": "passed",
                "outcome": "passed" if gate_passed else "failed",
                "failure_reason": (
                    None
                    if gate_passed
                    else "; ".join(trace_errors) or "shared evaluator gate not passed"
                ),
                "critic_feedback": None,
            }
        )
    return (assembler or ExistingSkillComparisonAssembler()).assemble(
        trigger,
        baseline,
        verified,
        evaluations,
        context_id=context_id,
        evaluation_window=evaluation_window,
        skill_code_versions={skill["id"]: skill["code"] for skill in skills},
    )
