"""Deterministic single-worker scheduler used by the Scheduling Arena."""

from __future__ import annotations

import copy
import math
import random
from dataclasses import dataclass, field
from typing import Any

POLICIES = ("fifo", "sjf", "priority", "edf", "hybrid")
INITIAL_SKILLS = ("fifo", "sjf", "priority", "edf")
EPSILON = 1e-9

POLICY_NAMES = {
    "fifo": "FIFO",
    "sjf": "SJF",
    "priority": "Priority",
    "edf": "EDF",
    "hybrid": "Hybrid",
}
POLICY_CODE = {
    "fifo": "def fifo_key(job):\n    return (job.arrival, job.id)\n",
    "sjf": "def sjf_key(job):\n    return (job.processing_time, job.arrival, job.id)\n",
    "priority": "def priority_key(job):\n    return (-job.priority, job.arrival, job.id)\n",
    "edf": "def edf_key(job):\n    return (job.deadline, job.arrival, job.id)\n",
    "hybrid": "def hybrid_key(job):\n    return (-job.priority, job.deadline, job.processing_time, job.arrival, job.id)\n",
}


class AdapterValidationError(ValueError):
    """Input or state validation failed without changing backend state."""


class AdapterOperationError(RuntimeError):
    """An operation failed and the caller must consider state uncertainty."""

    def __init__(self, message: str, *, state_uncertain: bool = True):
        super().__init__(message)
        self.state_uncertain = state_uncertain


def _number(value: Any, name: str, *, integer: bool = False) -> float | int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise AdapterValidationError(f"{name} must be a built-in number")
    if not math.isfinite(value):
        raise AdapterValidationError(f"{name} must be finite")
    if integer and (not isinstance(value, int) or isinstance(value, bool)):
        raise AdapterValidationError(f"{name} must be an integer")
    return value


@dataclass
class Job:
    id: str
    arrival: float
    processing_time: float
    priority: float
    deadline: float
    status: str = "scheduled"
    started_at: float | None = None
    completed_at: float | None = None
    dropped_at: float | None = None
    feasible: bool | None = None
    dispatched_policy_id: str | None = None
    segment_id: str | None = None

    @classmethod
    def from_input(cls, raw: dict[str, Any]) -> Job:
        if not isinstance(raw, dict):
            raise AdapterValidationError("job must be an object")
        required = ("id", "arrival", "processing_time", "priority", "deadline")
        missing = [key for key in required if key not in raw]
        if missing:
            raise AdapterValidationError(f"job missing fields: {', '.join(missing)}")
        job_id = raw["id"]
        if not isinstance(job_id, str) or not job_id.strip():
            raise AdapterValidationError("job id must be a non-empty string")
        arrival = float(_number(raw["arrival"], "arrival"))
        processing = float(_number(raw["processing_time"], "processing_time"))
        priority = float(_number(raw["priority"], "priority"))
        deadline = float(_number(raw["deadline"], "deadline"))
        if arrival < 0:
            raise AdapterValidationError("arrival must be non-negative")
        if processing <= 0:
            raise AdapterValidationError("processing_time must be positive")
        if deadline <= arrival:
            raise AdapterValidationError("deadline must be greater than arrival")
        return cls(job_id, arrival, processing, priority, deadline)

    def as_dict(self, now: float) -> dict[str, Any]:
        feasible = self.feasible
        if self.status == "pending":
            feasible = now + self.processing_time <= self.deadline + EPSILON
        elif self.status == "running":
            feasible = self.started_at + self.processing_time <= self.deadline + EPSILON
        return {
            "id": self.id,
            "arrival": self.arrival,
            "processing_time": self.processing_time,
            "priority": self.priority,
            "deadline": self.deadline,
            "status": self.status,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "dropped_at": self.dropped_at,
            "feasible": feasible,
            "dispatched_policy_id": self.dispatched_policy_id,
            "segment_id": self.segment_id,
        }


@dataclass
class Segment:
    id: str
    policy_id: str
    start: float
    end: float | None = None
    completed: int = 0
    expired: int = 0
    latencies: list[float] = field(default_factory=list)

    def as_dict(self, now: float) -> dict[str, Any]:
        return {
            "id": self.id,
            "policy_id": self.policy_id,
            "start": self.start,
            "end": self.end if self.end is not None else now,
            "metrics": {
                "completed": self.completed,
                "expired": self.expired,
                "p95_latency": _p95(self.latencies),
            },
        }


def _p95(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = 0.95 * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


class SchedulerBackend:
    """A serializable, deterministic SchedulerBackend implementation."""

    def __init__(self, seed: int = 42, initial_jobs: list[dict[str, Any]] | None = None):
        self._validate_seed(seed)
        self._seed = seed
        self._initial_jobs = None if initial_jobs is None else copy.deepcopy(initial_jobs)
        self._reset_state(seed, initial_jobs)

    @staticmethod
    def _validate_seed(seed: Any) -> None:
        if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
            raise AdapterValidationError("seed must be a non-negative integer")

    def _reset_state(self, seed: int, initial_jobs: list[dict[str, Any]] | None) -> None:
        self._validate_seed(seed)
        self._rng = random.Random(seed)
        self.run_id = f"run-{seed}-{self._rng.getrandbits(32):08x}"
        self.snapshot_version = 1
        self.time = 0.0
        self.policy_id = "fifo"
        self.previous_policy_id: str | None = None
        self.policy_reason = "初始策略"
        self.jobs: dict[str, Job] = {}
        self.events: list[dict[str, Any]] = []
        self.series: list[dict[str, Any]] = []
        self.segments = [Segment("segment-1", "fifo", 0.0)]
        self._paused_for_adaptation = False
        self._uses = {skill_id: 0 for skill_id in INITIAL_SKILLS}
        self._last_applied = {skill_id: None for skill_id in INITIAL_SKILLS}
        raw_jobs = self._default_jobs(seed) if initial_jobs is None else initial_jobs
        self._validate_batch(raw_jobs, allow_past=False)
        self.jobs = {job.id: job for job in (Job.from_input(raw) for raw in raw_jobs)}
        self._settle_current_time()
        self._record_series()

    @staticmethod
    def _default_jobs(seed: int) -> list[dict[str, Any]]:
        rng = random.Random(seed)
        jobs = []
        for index in range(8):
            arrival = float(index // 2)
            processing = float(1 + rng.randrange(5))
            jobs.append(
                {
                    "id": f"J{index + 1}",
                    "arrival": arrival,
                    "processing_time": processing,
                    "priority": float(1 + rng.randrange(5)),
                    "deadline": arrival + processing + float(5 + rng.randrange(8)),
                }
            )
        return jobs

    def _validate_batch(self, raw_jobs: Any, *, allow_past: bool) -> None:
        if not isinstance(raw_jobs, list):
            raise AdapterValidationError("jobs must be a list")
        if len(self.jobs) + len(raw_jobs) > 20:
            raise AdapterValidationError("job capacity is limited to 20")
        seen = set(self.jobs)
        parsed_ids = set()
        for raw in raw_jobs:
            job = Job.from_input(raw)
            if job.id in seen or job.id in parsed_ids:
                raise AdapterValidationError(f"duplicate job id: {job.id}")
            if not allow_past and job.arrival < self.time - EPSILON:
                raise AdapterValidationError("arrival cannot be earlier than current time")
            parsed_ids.add(job.id)

    def reset(self, seed: int = 42) -> dict[str, Any]:
        self._reset_state(seed, self._default_jobs(seed))
        return self.snapshot()

    def inject(self, jobs: list[dict[str, Any]]) -> dict[str, Any]:
        self._validate_batch(jobs, allow_past=False)
        new_jobs = [Job.from_input(raw) for raw in copy.deepcopy(jobs)]
        for job in new_jobs:
            self.jobs[job.id] = job
        self._settle_current_time()
        self._record_series()
        self.snapshot_version += 1
        return self.snapshot()

    def generate(self, count: int) -> dict[str, Any]:
        _number(count, "count", integer=True)
        if count not in (1, 4):
            raise AdapterValidationError("count must be 1 or 4")
        rng_state = self._rng.getstate()
        generated = []
        for _ in range(count):
            index = len(self.jobs) + len(generated) + 1
            processing = float(1 + self._rng.randrange(5))
            generated.append(
                {
                    "id": f"J{index}",
                    "arrival": self.time,
                    "processing_time": processing,
                    "priority": float(1 + self._rng.randrange(5)),
                    "deadline": self.time + processing + float(4 + self._rng.randrange(8)),
                }
            )
        try:
            return self.inject(generated)
        except Exception:
            self._rng.setstate(rng_state)
            raise

    def set_policy(self, policy_id: str, reason: str = "手動切換") -> dict[str, Any]:
        if policy_id not in INITIAL_SKILLS:
            raise AdapterValidationError("policy must be a verified Skill")
        if policy_id == self.policy_id:
            return self.snapshot()
        self.previous_policy_id = self.policy_id
        self.policy_id = policy_id
        self.policy_reason = reason
        self._close_segment()
        self._add_event("policy_changed", policy_id=policy_id, message=reason)
        self._settle_current_time()
        self._record_series()
        self.snapshot_version += 1
        return self.snapshot()

    def pause_for_adaptation(self) -> dict[str, Any]:
        self._paused_for_adaptation = True
        self.snapshot_version += 1
        return self.snapshot()

    def resume_after_adaptation(self) -> dict[str, Any]:
        self._paused_for_adaptation = False
        self.snapshot_version += 1
        return self.snapshot()

    def advance(self, dt: float) -> dict[str, Any]:
        dt = float(_number(dt, "dt"))
        if dt < 0:
            raise AdapterValidationError("dt must be non-negative")
        if self._paused_for_adaptation and dt > EPSILON:
            raise AdapterOperationError(
                "simulation is paused for adaptation", state_uncertain=False
            )
        target = round(self.time + dt, 10)
        while self.time < target - EPSILON:
            self._settle_current_time()
            next_times = [target]
            running = self._running_job()
            if running is not None:
                next_times.append(running.started_at + running.processing_time)
            next_times.extend(
                job.arrival for job in self.jobs.values() if job.status == "scheduled"
            )
            next_times.extend(job.deadline for job in self.jobs.values() if job.status == "pending")
            next_time = min(value for value in next_times if value > self.time + EPSILON)
            self.time = round(min(next_time, target), 10)
        self._settle_current_time()
        self._record_series()
        self.snapshot_version += 1
        return self.snapshot()

    def snapshot(self) -> dict[str, Any]:
        running = self._running_job()
        pending = [job for job in self.jobs.values() if job.status == "pending"]
        if running:
            worker_reason = f"正在處理 {running.id}"
        elif not self.jobs:
            worker_reason = "本局沒有訂單"
        elif any(job.status == "scheduled" for job in self.jobs.values()):
            worker_reason = "目前沒有可派工訂單：仍有訂單尚未到達"
        elif pending:
            worker_reason = "目前沒有可派工訂單：等待中的訂單皆無法準時完成"
        else:
            worker_reason = "本局工作皆已結束"
        metrics = self._metrics()
        policy = {
            "id": self.policy_id,
            "name": POLICY_NAMES[self.policy_id],
            "code": POLICY_CODE[self.policy_id],
            "previous_code": POLICY_CODE.get(self.previous_policy_id, ""),
            "reason": self.policy_reason,
        }
        return copy.deepcopy(
            {
                "run_id": self.run_id,
                "snapshot_version": self.snapshot_version,
                "time": self.time,
                "jobs": [job.as_dict(self.time) for job in self.jobs.values()],
                "worker": {
                    "job_id": running.id if running else None,
                    "state": "running" if running else "idle",
                    "reason": worker_reason,
                },
                "policy": policy,
                "metrics": metrics,
                "segments": [segment.as_dict(self.time) for segment in self.segments],
                "events": self.events,
                "series": self.series,
                "adaptation": {
                    "stage": "idle",
                    "message": "SP-01 未啟用 adaptation",
                    "adaptation_id": None,
                    "candidate_id": None,
                },
                "capacity": {
                    "total": len(self.jobs),
                    "limit": 20,
                    "remaining": 20 - len(self.jobs),
                },
            }
        )

    def list_skills(self) -> list[dict[str, Any]]:
        return copy.deepcopy(
            [
                {
                    "id": skill_id,
                    "name": POLICY_NAMES[skill_id],
                    "description": {
                        "fifo": "先到先服務",
                        "sjf": "先處理工時較短的訂單",
                        "priority": "優先度高者優先",
                        "edf": "截止時間較早者優先",
                    }[skill_id],
                    "code": POLICY_CODE[skill_id],
                    "source": "base",
                    "verified": True,
                    "uses": self._uses[skill_id],
                    "last_applied_at": self._last_applied[skill_id],
                }
                for skill_id in INITIAL_SKILLS
            ]
        )

    def _running_job(self) -> Job | None:
        return next((job for job in self.jobs.values() if job.status == "running"), None)

    def _settle_current_time(self) -> None:
        running = self._running_job()
        if running and self.time + EPSILON >= running.started_at + running.processing_time:
            running.status = "completed"
            running.completed_at = running.started_at + running.processing_time
            segment = self._segment_for(running.segment_id)
            segment.completed += 1
            segment.latencies.append(running.completed_at - running.arrival)
            self._add_event(
                "completed",
                job_id=running.id,
                policy_id=running.dispatched_policy_id,
                message="訂單完成",
            )
        for job in self.jobs.values():
            if job.status == "pending" and self.time + EPSILON >= job.deadline:
                job.status = "expired"
                job.dropped_at = job.deadline
                self._segment_for_expiry().expired += 1
                self._add_event("expired", job_id=job.id, message="截止後丟棄")
        for job in self.jobs.values():
            if job.status == "scheduled" and job.arrival <= self.time + EPSILON:
                job.status = "pending"
                self._add_event("arrived", job_id=job.id, message="訂單到達")
        if self._running_job() is None:
            eligible = [
                job
                for job in self.jobs.values()
                if job.status == "pending" and self._is_feasible(job)
            ]
            if eligible:
                job = min(eligible, key=self._policy_key)
                job.status = "running"
                job.started_at = self.time
                job.dispatched_policy_id = self.policy_id
                job.segment_id = self.segments[-1].id
                self._uses[self.policy_id] = self._uses.get(self.policy_id, 0) + 1
                self._last_applied[self.policy_id] = self.time
                self._add_event(
                    "started",
                    job_id=job.id,
                    policy_id=self.policy_id,
                    message=f"{POLICY_NAMES[self.policy_id]} 選中訂單",
                )

    def _is_feasible(self, job: Job) -> bool:
        return self.time + job.processing_time <= job.deadline + EPSILON

    def _policy_key(self, job: Job) -> tuple[Any, ...]:
        if self.policy_id == "fifo":
            return job.arrival, job.id
        if self.policy_id == "sjf":
            return job.processing_time, job.arrival, job.id
        if self.policy_id == "priority":
            return -job.priority, job.arrival, job.id
        if self.policy_id == "edf":
            return job.deadline, job.arrival, job.id
        return -job.priority, job.deadline, job.processing_time, job.arrival, job.id

    def _metrics(self) -> dict[str, Any]:
        completed = sum(job.status == "completed" for job in self.jobs.values())
        expired = sum(job.status == "expired" for job in self.jobs.values())
        latencies = [
            job.completed_at - job.arrival
            for job in self.jobs.values()
            if job.status == "completed"
        ]
        return {
            "completed": completed,
            "expired": expired,
            "throughput": completed / (self.time / 60) if self.time > EPSILON else None,
            "p95_latency": _p95(latencies),
        }

    def _record_series(self) -> None:
        metrics = self._metrics()
        point = {"time": self.time, **metrics}
        if self.series and abs(self.series[-1]["time"] - self.time) <= EPSILON:
            self.series[-1] = point
        else:
            self.series.append(point)

    def _add_event(
        self,
        event_type: str,
        *,
        job_id: str | None = None,
        policy_id: str | None = None,
        message: str,
    ) -> None:
        self.events.append(
            {
                "seq": len(self.events) + 1,
                "time": self.time,
                "type": event_type,
                "job_id": job_id,
                "policy_id": policy_id,
                "adaptation_id": None,
                "candidate_id": None,
                "message": message,
            }
        )

    def _close_segment(self) -> None:
        self.segments[-1].end = self.time
        self.segments.append(
            Segment(f"segment-{len(self.segments) + 1}", self.policy_id, self.time)
        )

    def _segment_for(self, segment_id: str | None) -> Segment:
        return next(segment for segment in self.segments if segment.id == segment_id)

    def _segment_for_expiry(self) -> Segment:
        return self.segments[-1]


def create_backend(
    seed: int = 42, initial_jobs: list[dict[str, Any]] | None = None
) -> SchedulerBackend:
    return SchedulerBackend(seed=seed, initial_jobs=initial_jobs)
