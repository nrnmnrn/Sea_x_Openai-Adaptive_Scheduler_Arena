from app import SessionController, build_app, render_metrics
from scheduler import create_backend


def test_scheduler_events_are_serialized_and_timer_starts_paused():
    demo = build_app(SessionController(create_backend(), "本機備援", "demo"))
    config = demo.get_config_file()

    timer = next(component for component in config["components"] if component["type"] == "timer")
    states = [component for component in config["components"] if component["type"] == "state"]
    assert timer["props"]["active"] is False
    assert len(states) == 2

    scheduler_events = [demo.fns[index] for index in range(9)]
    assert all(event.concurrency_id == "scheduler" for event in scheduler_events)
    assert all(event.concurrency_limit == 1 for event in scheduler_events)
    assert len(demo.fns) == 9
    assert demo.fns[8].trigger_mode == "always_last"


def test_single_step_stops_playback_and_stale_views_are_rejected():
    controller = SessionController(create_backend(), "local", "demo")
    first = controller.envelope()
    controller.toggle_play(True)
    stepped = controller.step()
    assert stepped["playing"] is False
    assert controller.accepts_view(stepped)
    assert not controller.accepts_view(first)


def test_metrics_render_includes_trends_segments_events_and_policy_reference():
    controller = SessionController(create_backend(), "local", "demo")
    controller.set_policy("sjf")
    rendered = render_metrics(controller.envelope())
    assert "Series trend" in rendered
    assert "Segment trend" in rendered
    assert "Recent events" in rendered
    assert "Policy diff" in rendered
    assert "--- previous_policy.py" in rendered


def test_controllers_are_independent():
    first = SessionController(create_backend(), "local", "demo")
    second = SessionController(create_backend(), "local", "demo")
    first.reset()
    first.inject(1)
    assert first.backend.snapshot()["capacity"]["total"] == 9
    assert second.backend.snapshot()["capacity"]["total"] == 8
