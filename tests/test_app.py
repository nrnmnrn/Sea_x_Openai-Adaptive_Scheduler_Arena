from app import (
    SessionController,
    build_app,
    load_backend_factory,
    render_metrics,
    render_skill_preview,
)
from scheduler import AdapterOperationError


def _job(job_id, arrival, processing_time, priority, deadline):
    return {
        "id": job_id,
        "arrival": arrival,
        "processing_time": processing_time,
        "priority": priority,
        "deadline": deadline,
    }


def test_scheduler_events_are_serialized_and_timer_starts_paused(backend_factory):
    demo = build_app(SessionController(backend_factory(), "本機備援", "demo"))
    config = demo.get_config_file()

    timer = next(component for component in config["components"] if component["type"] == "timer")
    states = [component for component in config["components"] if component["type"] == "state"]
    assert timer["props"]["active"] is False
    assert len(states) == 2

    scheduler_events = [event for event in demo.fns.values() if event.concurrency_id == "scheduler"]
    assert all(event.concurrency_id == "scheduler" for event in scheduler_events)
    assert all(event.concurrency_limit == 1 for event in scheduler_events)
    assert len(demo.fns) == 10
    assert demo.fns[8].trigger_mode == "always_last"


def test_single_step_stops_playback_and_stale_views_are_rejected(backend_factory):
    controller = SessionController(backend_factory(), "local", "demo")
    first = controller.envelope()
    controller.toggle_play(True)
    stepped = controller.step()
    assert stepped["playing"] is False
    assert controller.accepts_view(stepped)
    assert not controller.accepts_view(first)


def test_controller_replays_existing_skills_and_keeps_triggered_run_paused(backend_factory):
    backend = backend_factory(initial_jobs=[_job("A", 0, 10, 1, 2), _job("B", 0, 1, 2, 20)])
    controller = SessionController(backend, "local", "demo")
    controller.toggle_play(True)
    result = controller.advance(8)
    adaptation = result["snapshot"]["adaptation"]
    assert result["snapshot"]["time"] == 5
    assert adaptation["stage"] in {
        "existing_evaluation_passed",
        "existing_all_failed",
        "existing_evaluation_incomplete",
    }
    assert result["playing"] is False


def test_controller_reuses_real_replay_winner_and_resumes(backend_factory):
    jobs = [
        _job("J0", 3, 7, 1, 14),
        _job("J1", 2, 3, 2, 14),
        _job("J2", 3, 2, 1, 6),
        _job("J3", 1, 4, 1, 11),
        _job("J4", 0, 2, 4, 10),
        _job("J5", 4, 5, 4, 16),
        _job("J6", 4, 4, 4, 9),
        _job("J7", 2, 4, 3, 15),
        _job("J8", 1, 7, 2, 13),
        _job("J9", 0, 2, 7, 2),
        _job("J10", 4, 8, 7, 15),
    ]
    controller = SessionController(backend_factory(seed=0, initial_jobs=jobs), "local", "demo")
    controller.toggle_play(True)
    result = controller.advance(5)
    assert result["snapshot"]["adaptation"]["stage"] == "existing_skill_reused"
    assert result["snapshot"]["adaptation"]["candidate_id"] is None
    assert result["snapshot"]["adaptation"]["selected_skill_id"] == "sjf"
    assert result["snapshot"]["policy"]["id"] == "sjf"
    assert result["playing"] is True


def test_metrics_render_includes_trends_segments_events_and_policy_reference(backend_factory):
    controller = SessionController(backend_factory(), "local", "demo")
    controller.set_policy("sjf")
    rendered = render_metrics(controller.envelope())
    assert "Series trend" in rendered
    assert "Segment trend" in rendered
    assert "Recent events" in rendered
    assert "Policy diff" in rendered
    assert "--- previous_policy.py" in rendered
    assert "來源：base" in rendered
    assert "先到先服務" in render_skill_preview("fifo", controller.backend.list_skills())


def test_controllers_are_independent(backend_factory):
    first = SessionController(backend_factory(), "local", "demo")
    second = SessionController(backend_factory(), "local", "demo")
    first.reset()
    first.inject(1)
    assert first.backend.snapshot()["capacity"]["total"] == 9
    assert second.backend.snapshot()["capacity"]["total"] == 8


class FailingBackend:
    def __init__(self):
        self.snapshot_value = {"run_id": "run-1", "time": 0}
        self.reads_allowed = True

    def snapshot(self):
        if not self.reads_allowed:
            raise RuntimeError("snapshot unavailable")
        return dict(self.snapshot_value)

    def list_skills(self):
        if not self.reads_allowed:
            raise RuntimeError("skills unavailable")
        return [{"id": "fifo", "name": "FIFO"}]

    def advance(self, _dt):
        self.snapshot_value["time"] = 1
        raise AdapterOperationError("operation uncertain", state_uncertain=True)


def test_uncertain_operation_keeps_last_accepted_view():
    backend = FailingBackend()
    controller = SessionController(backend, "team", "demo")
    accepted = controller.envelope()
    backend.reads_allowed = False
    failed = controller.advance(1)
    assert failed["snapshot"] == accepted["snapshot"]
    assert failed["snapshot"]["time"] == 0
    assert failed["playing"] is False
    assert failed["error"] == "operation uncertain"


def test_backend_factory_is_preserved_for_new_sessions(monkeypatch):
    calls = []

    class Module:
        @staticmethod
        def create_backend(*, seed, initial_jobs):
            calls.append((seed, initial_jobs))
            return FailingBackend()

    monkeypatch.setattr("app.importlib.import_module", lambda _name: Module)
    factory, source = load_backend_factory("team", "team_backend:create_backend")
    assert source == "隊友後端"
    factory()
    factory()
    assert calls == [(42, None), (42, None)]
