from app import (
    SessionController,
    build_app,
    load_backend_factory,
    render_metrics,
    render_skill_preview,
)
from scheduler import AdapterOperationError


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
