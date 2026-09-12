"""Generate one untrusted policy draft with the Responses API; never execute it.

Run ``python -m experiments.openai_candidate_generation --prepare-only`` to inspect
the request, or provide ``OPENAI_API_KEY`` at runtime for one real request.
This is an experiment-local schema and ``choose_job`` signature, not an adapter.
"""

from __future__ import annotations

import argparse
import ast
import getpass
import json
import logging
import os
import sys
import warnings
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener
from uuid import uuid4

LOGGER = logging.getLogger(__name__)
API_URL = "https://api.openai.com/v1/responses"
MODEL = "gpt-6-astra"
EFFORT = "low"
SYNTHETIC_INPUT = {
    "experiment_only": True,
    "description": "Synthetic jobs; not all-skills-failed or evaluator evidence.",
    "jobs": [
        {
            "id": "urgent",
            "arrival": 0,
            "processing_time": 3,
            "priority": 9,
            "deadline": 6,
            "status": "pending",
        },
        {
            "id": "short",
            "arrival": 0,
            "processing_time": 1,
            "priority": 1,
            "deadline": 20,
            "status": "pending",
        },
    ],
    "now": 0,
}
SCHEMA = {
    "type": "object",
    "properties": {
        "reason": {"type": "string"},
        "policy_code": {"type": "string"},
        "workload_scope": {"type": "string"},
    },
    "required": ["reason", "policy_code", "workload_scope"],
    "additionalProperties": False,
}


class ExperimentError(RuntimeError):
    """A safe, user-facing failure from this isolated experiment."""


def build_request() -> dict[str, Any]:
    prompt = """Generate one policy draft for the supplied synthetic jobs. Return only the schema.
policy_code must define pure Python choose_job(jobs, now). Jobs are dictionaries with
id, arrival, processing_time, priority, deadline, and status. Consider only arrived,
pending, feasible jobs where now + processing_time <= deadline. Choose deterministically
by priority descending, then deadline, processing_time, arrival, and id. Return an ID or
None. Do not mutate input. Use no imports, I/O, or network access."""
    prompt += (
        " Do not define helper functions. reason 與 workload_scope 必須使用繁體中文；"
        "程式碼識別字保持 Python 英文。"
    )
    return {
        "model": MODEL,
        "reasoning": {"effort": EFFORT},
        "max_output_tokens": 4096,
        "store": False,
        "input": f"{prompt}\n\nSynthetic input:\n{json.dumps(SYNTHETIC_INPUT, sort_keys=True)}",
        "text": {
            "format": {
                "type": "json_schema",
                "name": "candidate_draft",
                "strict": True,
                "schema": SCHEMA,
            }
        },
    }


def _output_text(response: dict[str, Any]) -> str:
    if response.get("status") != "completed":
        raise ExperimentError("Responses API did not complete the request")
    output = response.get("output")
    if not isinstance(output, list):
        raise ExperimentError("Responses API returned an invalid response envelope")
    texts: list[str] = []
    for item in output:
        if not isinstance(item, dict):
            raise ExperimentError("Responses API returned an invalid response envelope")
        if item.get("type") != "message":
            continue
        content_items = item.get("content")
        if not isinstance(content_items, list):
            raise ExperimentError("Responses API returned an invalid response envelope")
        for content in content_items:
            if not isinstance(content, dict):
                raise ExperimentError("Responses API returned an invalid response envelope")
            if content.get("type") == "refusal":
                raise ExperimentError("Responses API returned a refusal")
            if content.get("type") == "output_text" and isinstance(content.get("text"), str):
                texts.append(content["text"])
    if not texts:
        raise ExperimentError("Responses API returned no output text")
    return "".join(texts)


def _draft(text: str) -> dict[str, str]:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as error:
        raise ExperimentError("Responses API returned invalid structured JSON") from error
    if not isinstance(value, dict) or set(value) != set(SCHEMA["required"]):
        raise ExperimentError("Responses API returned an unexpected draft shape")
    if any(
        not isinstance(value[name], str) or not value[name].strip() for name in SCHEMA["required"]
    ):
        raise ExperimentError("Responses API returned empty draft fields")
    return {name: value[name] for name in SCHEMA["required"]}


def syntax_check(policy_code: str) -> bool:
    """Check syntax and an experiment-local function shape; never execute code."""
    try:
        module = ast.parse(policy_code)
    except SyntaxError:
        return False
    if len(module.body) != 1 or not isinstance(module.body[0], ast.FunctionDef):
        return False
    functions = [module.body[0]]
    all_functions = [
        node
        for node in ast.walk(module)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    if (
        len(functions) != 1
        or len(all_functions) != 1
        or functions[0].name != "choose_job"
        or functions[0].decorator_list
        or any(isinstance(node, (ast.Import, ast.ImportFrom)) for node in ast.walk(module))
    ):
        return False
    arguments = functions[0].args
    return (
        not arguments.posonlyargs
        and [argument.arg for argument in arguments.args] == ["jobs", "now"]
        and not arguments.defaults
        and arguments.vararg is None
        and not arguments.kwonlyargs
        and arguments.kwarg is None
    )


Transport = Callable[[Request, float], Any]


class _RejectRedirects(HTTPRedirectHandler):
    def redirect_request(self, request: Request, *args: Any, **kwargs: Any) -> None:
        return None


def _open_without_redirects(request: Request, timeout: float) -> Any:
    return build_opener(_RejectRedirects()).open(request, timeout=timeout)


def generate(api_key: str, transport: Transport = _open_without_redirects) -> dict[str, Any]:
    if not api_key:
        raise ExperimentError("OPENAI_API_KEY is required unless --prepare-only is used")
    request = Request(
        API_URL,
        data=json.dumps(build_request()).encode(),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        response = transport(request, 60)
        try:
            status = response.getcode()
            if status < 200 or status >= 300:
                raise ExperimentError(f"Responses API returned HTTP status {status}")
            raw_payload = response.read()
        finally:
            close = getattr(response, "close", None)
            if callable(close):
                close()
    except HTTPError as error:
        raise ExperimentError(f"Responses API returned HTTP status {error.code}") from error
    except (URLError, TimeoutError, OSError) as error:
        raise ExperimentError("Responses API request failed") from error
    try:
        payload = json.loads(raw_payload.decode())
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ExperimentError("Responses API returned invalid JSON") from error
    if not isinstance(payload, dict):
        raise ExperimentError("Responses API returned an invalid response")
    draft = _draft(_output_text(payload))
    return {
        "experiment_only": True,
        "model": MODEL,
        "effort": EFFORT,
        "response_id": payload.get("id"),
        "usage": payload.get("usage"),
        "synthetic_input": SYNTHETIC_INPUT,
        "draft": draft,
        "syntax_check_passed": syntax_check(draft["policy_code"]),
        "evaluation_status": "unverified",
    }


def write_artifact(output_dir: Path, artifact: dict[str, Any]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    name = f"candidate-{datetime.now(UTC):%Y%m%dT%H%M%SZ}-{uuid4().hex}.json"
    target = output_dir / name
    with target.open("x", encoding="utf-8") as file:
        json.dump(artifact, file, indent=2, sort_keys=True)
        file.write("\n")
    return target


def _read_prompt_key() -> str:
    if not sys.stdin.isatty():
        raise ExperimentError("--prompt-key requires an interactive terminal")
    with warnings.catch_warnings():
        warnings.simplefilter("error", getpass.GetPassWarning)
        try:
            return getpass.getpass("OPENAI_API_KEY: ")
        except (getpass.GetPassWarning, EOFError) as error:
            raise ExperimentError("--prompt-key could not read hidden terminal input") from error


def read_env_key(path: Path) -> str:
    """Read one conventional dotenv key as plain text without mutating the environment."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise ExperimentError("--env-file could not be read") from error
    values: dict[str, str] = {}
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        key, separator, value = line.partition("=")
        if separator and key.strip() in {"OPENAI_API_KEY", "openai_api_key"}:
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
                value = value[1:-1]
            values[key.strip()] = value
    key = values.get("OPENAI_API_KEY", values.get("openai_api_key", ""))
    if not key:
        raise ExperimentError("--env-file does not contain an OpenAI API key")
    return key


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(
        description="Run one isolated, untrusted OpenAI policy-draft experiment."
    )
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/planner-experiment"))
    parser.add_argument(
        "--prepare-only",
        action="store_true",
        help="write the request JSON without a key or network",
    )
    key_source = parser.add_mutually_exclusive_group()
    key_source.add_argument(
        "--prompt-key", action="store_true", help="read the API key from hidden terminal input"
    )
    key_source.add_argument("--env-file", type=Path, help="read an API key from this dotenv file")
    args = parser.parse_args(argv)
    try:
        if args.prepare_only:
            path = write_artifact(
                args.output_dir, {"experiment_only": True, "request": build_request()}
            )
            LOGGER.info("Wrote request artifact to %s", path)
            return 0
        key = (
            _read_prompt_key()
            if args.prompt_key
            else read_env_key(args.env_file)
            if args.env_file
            else os.environ.get("OPENAI_API_KEY", "")
        )
        artifact = generate(key)
        path = write_artifact(args.output_dir, artifact)
    except (ExperimentError, EOFError) as error:
        LOGGER.error("Candidate generation experiment failed: %s", error)
        return 1
    except OSError:
        LOGGER.error("Candidate generation experiment could not write its artifact")
        return 1
    if not artifact["syntax_check_passed"]:
        LOGGER.error(
            "Candidate generation experiment produced an invalid syntax or function shape: %s",
            path,
        )
        return 2
    LOGGER.info("Wrote unverified candidate artifact to %s", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
