"""Gradio entry point for the Scheduling Arena."""

from __future__ import annotations

import argparse
import difflib
import importlib
from collections.abc import Callable
from typing import Any

from scheduler import POLICY_NAMES, create_backend


class SessionController:
    def __init__(self, backend: Any, source: str, mode: str):
        self.backend = backend
        self.source = source
        self.mode = mode
        self.generation = 0
        self.revision = 0
        self.playing = False
        self.speed = 1.0

    def envelope(
        self, snapshot: dict[str, Any] | None = None, error: str | None = None
    ) -> dict[str, Any]:
        snapshot = snapshot or self.backend.snapshot()
        self.revision += 1
        return {
            "snapshot": snapshot,
            "skills": self.backend.list_skills(),
            "session_generation": self.generation,
            "revision": self.revision,
            "backend_source": self.source,
            "playing": self.playing,
            "speed": self.speed,
            "error": error,
        }

    def call(self, operation: Callable[[], dict[str, Any]]) -> dict[str, Any]:
        try:
            return self.envelope(operation())
        except (ValueError, RuntimeError) as exc:
            self.playing = False
            return self.envelope(error=str(exc))

    def reset(self) -> dict[str, Any]:
        self.playing = False
        self.generation += 1
        return self.call(lambda: self.backend.reset())

    def advance(self, dt: float) -> dict[str, Any]:
        return self.call(lambda: self.backend.advance(dt))

    def step(self) -> dict[str, Any]:
        self.playing = False
        return self.advance(1)

    def inject(self, count: int) -> dict[str, Any]:
        return self.call(lambda: self.backend.generate(count))

    def set_policy(self, policy_id: str) -> dict[str, Any]:
        if self.mode != "developer":
            return self.envelope(error="Demo mode 不提供手動策略切換")
        return self.call(lambda: self.backend.set_policy(policy_id, "Developer mode 套用技能"))

    def toggle_play(self, playing: bool) -> dict[str, Any]:
        self.playing = playing
        return self.envelope()

    def set_speed(self, speed: float) -> dict[str, Any]:
        self.speed = speed
        return self.envelope()

    def accepts_view(self, envelope: dict[str, Any]) -> bool:
        snapshot = envelope.get("snapshot", {})
        return (
            envelope.get("session_generation") == self.generation
            and envelope.get("revision") == self.revision
            and snapshot.get("run_id") == self.backend.snapshot().get("run_id")
        )


def load_backend(backend_name: str, factory_path: str | None) -> tuple[Any, str]:
    if backend_name == "local":
        return create_backend(), "本機備援"
    if backend_name != "team":
        raise ValueError("backend 必須是 local 或 team")
    if not factory_path or ":" not in factory_path:
        raise ValueError("team backend 必須提供 --factory module:function")
    module_name, function_name = factory_path.split(":", 1)
    module = importlib.import_module(module_name)
    factory = getattr(module, function_name, None)
    if not callable(factory):
        raise TypeError(f"找不到可呼叫的 factory：{factory_path}")
    return factory(seed=42, initial_jobs=None), "隊友後端"


def render_arena(envelope: dict[str, Any]) -> str:
    snapshot = envelope["snapshot"]
    jobs = snapshot["jobs"]
    active = sorted(
        (job for job in jobs if job["status"] not in ("completed", "expired")),
        key=lambda job: (
            {"running": 0, "pending": 1, "scheduled": 2}[job["status"]],
            job["arrival"],
            job["id"],
        ),
    )
    rows = []
    for job in active:
        status = job["status"]
        position = 0.0
        waiting_text = ""
        if status == "pending":
            position = max(
                0,
                min(
                    100,
                    (snapshot["time"] - job["arrival"]) / (job["deadline"] - job["arrival"]) * 100,
                ),
            )
            waiting_text = "可準時完成" if job["feasible"] else "已無法準時完成"
        elif status == "running":
            position = max(
                0, min(100, (snapshot["time"] - job["started_at"]) / job["processing_time"] * 100)
            )
            waiting_text = "處理中"
        else:
            waiting_text = f"抵達倒數 {max(0, job['arrival'] - snapshot['time']):.1f} 秒"
        marker = f"<i style='left:{position:.1f}%'></i>" if status != "scheduled" else ""
        rows.append(
            f"""
            <article class='job-row {status}'>
              <div class='job-label'><strong>{job["id"]}</strong><span>P{job["priority"]} · {job["processing_time"]:.1f}s</span></div>
              <div class='job-tracks'>
                <div class='track-caption'>等待 → deadline <b>{waiting_text}</b></div>
                <div class='track waiting-track'>{marker}<span class='job-pill'>{job["id"]}</span></div>
                <div class='track-caption'>處理 → EXIT</div>
                <div class='track processing-track'>{marker if status == "running" else ""}<span class='worker-dot'>⚙</span><span class='exit-label'>EXIT →</span></div>
              </div>
              <div class='job-deadline'>截止 t={job["deadline"]:.1f}<br><span>逾時回收</span></div>
              <div class='trash'>♜</div>
            </article>
            """
        )
    history = [job for job in jobs if job["status"] in ("completed", "expired")]
    history_text = (
        "".join(
            f"<span class='history-chip'>{job['id']} {'EXIT ✓' if job['status'] == 'completed' else '回收'} · t={job['completed_at'] or job['dropped_at']:.1f}</span>"
            for job in history
        )
        or "<span class='muted'>尚無結束訂單</span>"
    )
    metrics = snapshot["metrics"]
    cards = (
        ("完成", metrics["completed"], "件", "good"),
        ("逾期", metrics["expired"], "件", "warn"),
        (
            "吞吐量",
            "—" if metrics["throughput"] is None else f"{metrics['throughput']:.2f}",
            "件／分",
            "neutral",
        ),
        (
            "P95 延遲",
            "—" if metrics["p95_latency"] is None else f"{metrics['p95_latency']:.2f}",
            "秒",
            "neutral",
        ),
    )
    card_html = "".join(
        f"<div class='metric-card {tone}'><small>{label}</small><b>{value}</b><span>{unit}</span></div>"
        for label, value, unit, tone in cards
    )
    return f"""
    <style>
      .arena {{ background:linear-gradient(118deg,#11253b 0%,#142a43 48%,#204b66 100%); color:#edf5f5; padding:16px 14px 12px; border:1px solid #274962; border-radius:12px; box-shadow:0 18px 50px #07111d80; }}
      .arena-head {{ display:flex; justify-content:space-between; gap:16px; align-items:flex-start; padding:0 2px 12px; border-bottom:1px solid #35546b; }}
      .arena-title {{ font-size:18px; font-weight:800; letter-spacing:.03em; }}
      .arena-subtitle,.muted {{ color:#8fa8b7; font-size:11px; }}
      .arena-meta {{ color:#e0ac53; font-size:11px; white-space:nowrap; }}
      .metric-grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:6px; margin:10px 0; }}
      .metric-card {{ min-height:48px; padding:8px 10px; border:1px solid #2f5068; border-radius:7px; background:#162e47b8; display:flex; flex-direction:column; }}
      .metric-card small,.metric-card span {{ color:#8fa8b7; font-size:10px; }} .metric-card b {{ color:#a8d8cf; font-size:17px; line-height:20px; }} .metric-card.warn b {{ color:#e5b361; }}
      .worker-status {{ border:1px solid #31546a; border-radius:7px; padding:6px 10px; color:#b4c8d2; font-size:11px; margin-bottom:8px; }}
      .job-list {{ max-height:400px; overflow-y:auto; padding:3px 4px 2px 0; scrollbar-color:#4d7890 #122840; }}
      .job-row {{ min-width:640px; display:grid; grid-template-columns:185px minmax(360px,1fr) 105px 25px; gap:10px; align-items:center; padding:8px 4px; border-bottom:1px solid #29475c; }}
      .job-label strong {{ display:block; font-size:14px; color:#eef6f8; }} .job-label span {{ color:#91adbb; font-size:10px; }}
      .job-tracks {{ display:grid; grid-template-columns:115px 1fr; gap:3px 8px; align-items:center; }}
      .track-caption {{ color:#91adbb; font-size:10px; }} .track-caption b {{ display:block; color:#d0dfdf; font-weight:500; }}
      .track {{ position:relative; height:25px; border:1px solid #315773; border-radius:13px; background:#173650; overflow:visible; }}
      .job-pill {{ position:absolute; left:8%; top:2px; padding:4px 9px; border-radius:13px; background:#8297a1; color:#102333; font-size:10px; font-weight:800; }}
      .pending .job-pill {{ background:#84c9bb; }} .running .job-pill {{ background:#e4b15b; }} .scheduled .job-pill {{ background:#84949e; }}
      .track i {{ position:absolute; top:0; bottom:0; width:3px; background:#84c9bb; border-radius:2px; }}
      .processing-track {{ border-style:dashed; border-color:#996c37; }} .worker-dot {{ position:absolute; left:45%; top:3px; color:#e0ad5c; }} .exit-label {{ position:absolute; right:8px; top:5px; color:#8fd4c2; font-size:10px; font-weight:700; }}
      .job-deadline {{ color:#b6c7ce; font-size:10px; line-height:15px; }} .job-deadline span {{ color:#869ca7; }} .trash {{ color:#bd8392; font-size:19px; transform:rotate(180deg); }}
      .history {{ display:flex; gap:6px; flex-wrap:wrap; border-top:1px solid #31546a; margin-top:4px; padding-top:9px; }} .history-chip {{ border:1px solid #3a665d; color:#a9d5cb; border-radius:10px; padding:3px 8px; font-size:10px; }}
      @media (max-width:800px) {{ .metric-grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} .arena-head {{ flex-direction:column; }} }}
    </style>
    <div class='arena'>
      <div class='arena-head'><div><div class='arena-title'>排程輸送帶</div><div class='arena-subtitle'>本局 {len(jobs)}/20 · 剩餘名額 {snapshot["capacity"]["remaining"]}</div></div><div class='arena-meta'>t={snapshot["time"]:.1f} sec · {"播放中" if envelope["playing"] else "已暫停"} · {snapshot["policy"]["name"]} · {snapshot["policy"]["reason"]}</div></div>
      <div class='metric-grid'>{card_html}</div>
      <div class='worker-status'>◉ {snapshot["worker"]["reason"]}</div>
      <div class='job-list'>{"".join(rows) or "<p class='muted'>輸送帶目前沒有進行中的工作</p>"}</div>
      <div class='history'>歷史：{history_text}</div>
    </div>
    """


def _render_metrics_legacy(envelope: dict[str, Any]) -> str:
    snapshot = envelope["snapshot"]
    metrics = snapshot["metrics"]
    skills = envelope["skills"]
    code = snapshot["policy"]["code"]
    skill_text = "\n".join(
        f"- {skill['name']}：使用 {skill['uses']} 次，來源 {skill['source']}" for skill in skills
    )
    return f"""### Metrics

| 完成數 | 逾期數 | 吞吐量（件／分） | P95 完成延遲（秒） |
|---:|---:|---:|---:|
| {metrics["completed"]} | {metrics["expired"]} | {metrics["throughput"] if metrics["throughput"] is not None else "—"} | {metrics["p95_latency"] if metrics["p95_latency"] is not None else "—"} |

### 實際 Policy code

```python
{code}
```

### Skill Library 摘要

{skill_text}
"""


def render_metrics(envelope: dict[str, Any]) -> str:
    snapshot = envelope["snapshot"]
    metrics = snapshot["metrics"]
    policy = snapshot["policy"]
    previous_code = policy.get("previous_code") or ""
    policy_diff = (
        "".join(
            difflib.unified_diff(
                previous_code.splitlines(keepends=True),
                policy["code"].splitlines(keepends=True),
                fromfile="previous_policy.py",
                tofile="current_policy.py",
            )
        )
        or "（尚未切換 Policy，沒有差異）"
    )
    series_rows = (
        "\n".join(
            f"| {point['time']:.1f} | {point['completed']} | {point['expired']} | "
            f"{point['throughput'] if point['throughput'] is not None else '—'} | "
            f"{point['p95_latency'] if point['p95_latency'] is not None else '—'} |"
            for point in snapshot["series"][-20:]
        )
        or "| — | — | — | — | — |"
    )
    segment_rows = (
        "\n".join(
            f"| {segment['id']} | {segment['policy_id']} | {segment['start']:.1f} | "
            f"{segment['end']:.1f} | {segment['metrics']['completed']} | "
            f"{segment['metrics']['expired']} |"
            for segment in snapshot["segments"]
        )
        or "| — | — | — | — | — | — |"
    )
    event_rows = (
        "\n".join(
            f"| {event['seq']} | {event['time']:.1f} | {event['type']} | "
            f"{event.get('job_id') or '—'} | {event.get('policy_id') or '—'} |"
            for event in snapshot["events"][-60:]
        )
        or "| — | — | — | — | — |"
    )
    skill_text = "\n".join(
        f"- {skill['name']}嚗蝙??{skill['uses']} 甈∴?靘? {skill['source']}"
        for skill in envelope["skills"]
    )
    return f"""### Metrics & Code

Live metrics: completed `{metrics["completed"]}`, expired `{metrics["expired"]}`, throughput `{metrics["throughput"] or "—"}`, P95 latency `{metrics["p95_latency"] or "—"}`

Snapshot: `{snapshot["run_id"]}` / revision `{envelope["revision"]}` / time `{snapshot["time"]:.1f}`

### Series trend (latest 20 points)

| time | completed | expired | throughput | P95 latency |
|---:|---:|---:|---:|---:|
{series_rows}

### Segment trend and Policy attribution

| segment | Policy | start | end | completed | expired |
|---|---|---:|---:|---:|---:|
{segment_rows}

### Recent events (latest 60)

| seq | time | type | Job | Policy |
|---:|---:|---|---|---|
{event_rows}

### Current Policy code: {policy["name"]}

```python
{policy["code"]}
```

### Previous Policy code (diff reference)

```python
{policy.get("previous_code") or "尚未切換 Policy"}
```

### Policy diff

```diff
{policy_diff}
```

### Skill Library

{skill_text}
"""


APP_CSS = """
body { background:#171719 !important; }
.gradio-container { max-width:1320px !important; padding-top:28px !important; color:#e8e9ec; }
.gradio-container, .gradio-container * { font-family: Inter, ui-sans-serif, system-ui, sans-serif; }
.gradio-container h1 { font-size:24px !important; letter-spacing:.02em; }
.gradio-container .tabs { border-bottom:1px solid #3b3b40; }
.gradio-container button { border:1px solid #45454b !important; background:#4a4a50 !important; color:#f1f1f2 !important; border-radius:5px !important; min-height:38px; }
.gradio-container button:hover { border-color:#c56622 !important; }
.gradio-container button.primary { background:#c56622 !important; border-color:#c56622 !important; }
.gradio-container input, .gradio-container textarea, .gradio-container .wrap { background:#242426 !important; border-color:#424247 !important; color:#ececef !important; }
.gradio-container .tab-nav button.selected { color:#d6782e !important; border-bottom-color:#d6782e !important; }
"""


def build_app(
    controller: SessionController | None = None,
    controller_factory: Callable[[], SessionController] | None = None,
):
    import gradio as gr

    if controller is None and controller_factory is None:
        raise ValueError("controller or controller_factory is required")
    if controller is None:
        controller = controller_factory()
    if controller_factory is None:
        controller_factory = lambda: SessionController(
            create_backend(), controller.source, controller.mode
        )
    initial = controller.envelope()
    with gr.Blocks(title="Adaptive Scheduler Arena") as demo:
        controller_state = gr.State(None)
        view_state = gr.State(None)
        gr.Markdown(
            f"# Adaptive Scheduler Arena\n資料來源：{controller.source}　`MOCK 示範`　模式：{controller.mode}"
        )
        with gr.Tab("Scheduling Arena"):
            with gr.Row():
                play = gr.Button("播放")
                pause = gr.Button("暫停")
                step = gr.Button("單步 +1")
                reset = gr.Button("重設")
                speed = gr.Dropdown([0.5, 1.0, 2.0], value=1.0, label="倍速")
            with gr.Row():
                one = gr.Button("新增 1 筆")
                flash = gr.Button("Flash Sale 4 筆")
                policy = gr.Dropdown(
                    list(INITIAL_POLICY_CHOICES),
                    value="fifo",
                    label="Developer Policy",
                    visible=controller.mode == "developer",
                )
                apply = gr.Button("套用技能", visible=controller.mode == "developer")
            source = gr.Markdown(f"資料來源：{controller.source}；`MOCK 示範`；目前狀態：paused")
            arena = gr.HTML(render_arena(initial))
            status = gr.JSON(initial)

            def update(envelope):
                source_text = f"資料來源：{controller.source}；`MOCK 示範`；狀態：{'playing' if envelope['playing'] else 'paused'}"
                return (
                    render_arena(envelope),
                    envelope,
                    source_text,
                    render_metrics(envelope),
                    envelope["skills"],
                )

            def resolve_controller(current):
                return current if current is not None else controller_factory()

            def run_operation(current, previous_view, operation):
                active_controller = resolve_controller(current)
                if previous_view is not None and not active_controller.accepts_view(previous_view):
                    envelope = active_controller.envelope(error="已拒收過時的 session 回應")
                else:
                    envelope = operation(active_controller)
                return (
                    active_controller,
                    envelope,
                    *update(envelope),
                    gr.Timer(active=envelope["playing"]),
                )

            def tick(current, previous_view):
                active_controller = resolve_controller(current)
                if previous_view is not None and not active_controller.accepts_view(previous_view):
                    envelope = active_controller.envelope(error="已拒收過時的 session 回應")
                elif active_controller.playing:
                    envelope = active_controller.advance(0.2 * active_controller.speed)
                else:
                    envelope = active_controller.envelope()
                return active_controller, envelope, *update(envelope)

            scheduler_event = {"concurrency_id": "scheduler", "concurrency_limit": 1}
            timer = gr.Timer(0.2, active=False)
        with gr.Tab("Metrics & Code"):
            metrics = gr.Markdown(render_metrics(initial))
        with gr.Tab("Skill Library"):
            library = gr.JSON(initial["skills"])

        scheduler_inputs = [controller_state, view_state]
        scheduler_outputs = [
            controller_state,
            view_state,
            arena,
            status,
            source,
            metrics,
            library,
            timer,
        ]
        play.click(
            lambda current, previous: run_operation(
                current, previous, lambda active: active.toggle_play(True)
            ),
            inputs=scheduler_inputs,
            outputs=scheduler_outputs,
            **scheduler_event,
        )
        pause.click(
            lambda current, previous: run_operation(
                current, previous, lambda active: active.toggle_play(False)
            ),
            inputs=scheduler_inputs,
            outputs=scheduler_outputs,
            **scheduler_event,
        )
        step.click(
            lambda current, previous: run_operation(
                current, previous, lambda active: active.step()
            ),
            inputs=scheduler_inputs,
            outputs=scheduler_outputs,
            **scheduler_event,
        )
        reset.click(
            lambda current, previous: run_operation(
                current, previous, lambda active: active.reset()
            ),
            inputs=scheduler_inputs,
            outputs=scheduler_outputs,
            **scheduler_event,
        )
        one.click(
            lambda current, previous: run_operation(
                current, previous, lambda active: active.inject(1)
            ),
            inputs=scheduler_inputs,
            outputs=scheduler_outputs,
            **scheduler_event,
        )
        flash.click(
            lambda current, previous: run_operation(
                current, previous, lambda active: active.inject(4)
            ),
            inputs=scheduler_inputs,
            outputs=scheduler_outputs,
            **scheduler_event,
        )
        speed.change(
            lambda value, current, previous: run_operation(
                current, previous, lambda active: active.set_speed(float(value))
            ),
            inputs=[speed, *scheduler_inputs],
            outputs=scheduler_outputs,
            **scheduler_event,
        )
        apply.click(
            lambda value, current, previous: run_operation(
                current, previous, lambda active: active.set_policy(value)
            ),
            inputs=[policy, *scheduler_inputs],
            outputs=scheduler_outputs,
            **scheduler_event,
        )
        timer.tick(
            tick,
            inputs=scheduler_inputs,
            outputs=[controller_state, view_state, arena, status, source, metrics, library],
            trigger_mode="always_last",
            **scheduler_event,
        )
    return demo


INITIAL_POLICY_CHOICES = [
    (POLICY_NAMES[policy_id], policy_id) for policy_id in ("fifo", "sjf", "priority", "edf")
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", required=True, choices=("local", "team"))
    parser.add_argument("--factory")
    parser.add_argument("--mode", choices=("demo", "developer"), default="demo")
    parser.add_argument("--port", type=int, default=7860)
    args = parser.parse_args()
    backend, source = load_backend(args.backend, args.factory)
    build_app(SessionController(backend, source, args.mode)).launch(
        server_name="127.0.0.1", server_port=args.port, share=False, css=APP_CSS
    )


if __name__ == "__main__":
    main()
