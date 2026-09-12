from app import SessionController, build_app
from scheduler import create_backend


def test_scheduler_events_are_serialized_and_timer_starts_paused():
    demo = build_app(SessionController(create_backend(), "本機備援", "demo"))
    config = demo.get_config_file()

    timer = next(component for component in config["components"] if component["type"] == "timer")
    assert timer["props"]["active"] is False

    scheduler_events = [demo.fns[index] for index in range(9)]
    assert all(event.concurrency_id == "scheduler" for event in scheduler_events)
    assert all(event.concurrency_limit == 1 for event in scheduler_events)
    assert len(demo.fns) == 9
    assert demo.fns[8].trigger_mode == "always_last"
