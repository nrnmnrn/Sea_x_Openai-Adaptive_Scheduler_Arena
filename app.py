"""Gradio entry point for the Scheduling Arena."""

from __future__ import annotations

import argparse
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
    active = [job for job in jobs if job["status"] not in ("completed", "expired")]
    rows = []
    for job in active:
        status = job["status"]
        position = 0
        if status == "pending":
            position = max(
                0,
                min(
                    100,
                    (snapshot["time"] - job["arrival"]) / (job["deadline"] - job["arrival"]) * 100,
                ),
            )
        elif status == "running":
            position = max(
                0, min(100, (snapshot["time"] - job["started_at"]) / job["processing_time"] * 100)
            )
        rows.append(
            f"<div class='job {status}'><b>{job['id']}</b> · P{job['priority']} · 工時 {job['processing_time']} · deadline {job['deadline']} · {status} <span style='left:{position:.1f}%'>&nbsp;</span></div>"
        )
    history = [job for job in jobs if job["status"] in ("completed", "expired")]
    history_text = (
        "、".join(
            f"{job['id']} {'EXIT ✓' if job['status'] == 'completed' else '垃圾桶／回收'}"
            for job in history
        )
        or "尚無結束訂單"
    )
    return f"""
    <style>
      .arena {{ background:#0d1b2a; color:#f4f7fb; padding:18px; border-radius:12px; }}
      .lane {{ border-bottom:2px solid #6c7a89; padding:12px 0; margin:10px 0; }}
      .job {{ position:relative; margin:7px 0; padding:9px; border-radius:6px; background:#44515e; }}
      .job.pending {{ background:#287d5a; }} .job.running {{ background:#b88718; color:#111; }}
      .job span {{ position:absolute; width:10px; height:10px; border-radius:50%; background:#fff; top:14px; }}
      .meta {{ display:flex; gap:28px; flex-wrap:wrap; }}
    </style>
    <div class='arena'>
      <div class='meta'><b>策略：{snapshot["policy"]["name"]}</b><b>t={snapshot["time"]:.2f}</b><b>名額：{snapshot["capacity"]["remaining"]}</b></div>
      <div class='lane'>等待帶 ───────── 垃圾桶（截止後丟棄）</div>
      {"".join(rows) or "<p>目前沒有活動訂單</p>"}
      <div class='lane'>Worker → ⚙ → EXIT</div>
      <p>Worker：{snapshot["worker"]["reason"]}</p>
      <p>本局歷史：{history_text}</p>
    </div>
    """


def render_metrics(envelope: dict[str, Any]) -> str:
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


def build_app(controller: SessionController):
    import gradio as gr

    initial = controller.envelope()
    with gr.Blocks(title="Adaptive Scheduler Arena") as demo:
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
                return render_arena(envelope), envelope, source_text

            def tick():
                if controller.playing:
                    return update(controller.advance(0.2 * controller.speed))
                return update(controller.envelope())

            play.click(
                lambda: update(controller.toggle_play(True)), outputs=[arena, status, source]
            )
            pause.click(
                lambda: update(controller.toggle_play(False)), outputs=[arena, status, source]
            )
            step.click(lambda: update(controller.advance(1)), outputs=[arena, status, source])
            reset.click(lambda: update(controller.reset()), outputs=[arena, status, source])
            one.click(lambda: update(controller.inject(1)), outputs=[arena, status, source])
            flash.click(lambda: update(controller.inject(4)), outputs=[arena, status, source])
            speed.change(
                lambda value: update(controller.set_speed(float(value))),
                inputs=speed,
                outputs=[arena, status, source],
            )
            apply.click(
                lambda value: update(controller.set_policy(value)),
                inputs=policy,
                outputs=[arena, status, source],
            )
            timer = gr.Timer(0.2)
            timer.tick(tick, outputs=[arena, status, source])
        with gr.Tab("Metrics & Code"):
            metrics = gr.Markdown(render_metrics(initial))
            status.change(lambda value: render_metrics(value), inputs=status, outputs=metrics)
        with gr.Tab("Skill Library"):
            library = gr.JSON(initial["skills"])
            status.change(lambda value: value["skills"], inputs=status, outputs=library)
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
        server_name="127.0.0.1", server_port=args.port, share=False
    )


if __name__ == "__main__":
    main()
