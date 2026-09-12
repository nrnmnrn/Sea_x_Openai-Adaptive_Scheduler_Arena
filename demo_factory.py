"""Repeatable built-in policy adaptation demo workload."""

from scheduler import SchedulerBackend

DEMO_JOBS = [
    {"id": "J0", "arrival": 3, "processing_time": 7, "priority": 1, "deadline": 14},
    {"id": "J1", "arrival": 2, "processing_time": 3, "priority": 2, "deadline": 14},
    {"id": "J2", "arrival": 3, "processing_time": 2, "priority": 1, "deadline": 6},
    {"id": "J3", "arrival": 1, "processing_time": 4, "priority": 1, "deadline": 11},
    {"id": "J4", "arrival": 0, "processing_time": 2, "priority": 4, "deadline": 10},
    {"id": "J5", "arrival": 4, "processing_time": 5, "priority": 4, "deadline": 16},
    {"id": "J6", "arrival": 4, "processing_time": 4, "priority": 4, "deadline": 9},
    {"id": "J7", "arrival": 2, "processing_time": 4, "priority": 3, "deadline": 15},
    {"id": "J8", "arrival": 1, "processing_time": 7, "priority": 2, "deadline": 13},
    {"id": "J9", "arrival": 0, "processing_time": 2, "priority": 7, "deadline": 2},
    {"id": "J10", "arrival": 4, "processing_time": 8, "priority": 7, "deadline": 15},
]


def create_backend(*, seed: int = 0, initial_jobs=None):
    return SchedulerBackend(
        seed=seed, initial_jobs=DEMO_JOBS if initial_jobs is None else initial_jobs
    )
