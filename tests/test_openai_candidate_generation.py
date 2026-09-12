import getpass
import json
import warnings
from pathlib import Path
from urllib.request import Request

import pytest

import experiments.openai_candidate_generation as experiment
from experiments.openai_candidate_generation import (
    API_URL,
    SYNTHETIC_INPUT,
    ExperimentError,
    _read_prompt_key,
    _RejectRedirects,
    build_request,
    generate,
    read_env_key,
    syntax_check,
)


class StubResponse:
    def __init__(self, payload: dict, status: int = 200) -> None:
        self.payload = payload
        self.status = status

    def getcode(self) -> int:
        return self.status

    def read(self) -> bytes:
        return json.dumps(self.payload).encode()


class RawResponse(StubResponse):
    def __init__(self, payload: bytes) -> None:
        self.payload = payload
        self.status = 200

    def read(self) -> bytes:
        return self.payload


def completed(policy_code: str) -> dict:
    return {
        "id": "resp_test",
        "status": "completed",
        "usage": {"input_tokens": 1},
        "output": [
            {
                "type": "message",
                "content": [
                    {
                        "type": "output_text",
                        "text": json.dumps(
                            {
                                "reason": "urgent first",
                                "policy_code": policy_code,
                                "workload_scope": "synthetic",
                            }
                        ),
                    }
                ],
            }
        ],
    }


def test_request_uses_fixed_responses_model_and_strict_schema() -> None:
    request = build_request()

    assert request["model"] == "gpt-6-astra"
    assert request["reasoning"] == {"effort": "low"}
    assert request["max_output_tokens"] == 4096
    assert request["store"] is False
    assert request["text"]["format"]["strict"] is True
    assert request["text"]["format"]["schema"]["required"] == [
        "reason",
        "policy_code",
        "workload_scope",
    ]


def test_generate_sends_one_request_and_keeps_result_unverified() -> None:
    calls = []
    code = "def choose_job(jobs, now):\n    return None\n"

    def transport(request, timeout):
        calls.append((request, timeout))
        return StubResponse(completed(code))

    artifact = generate("test-key", transport)

    assert len(calls) == 1
    assert calls[0][0].full_url == API_URL
    assert calls[0][1] == 60
    assert json.loads(calls[0][0].data)["model"] == "gpt-6-astra"
    assert artifact["synthetic_input"] == SYNTHETIC_INPUT
    assert artifact["evaluation_status"] == "unverified"
    assert artifact["syntax_check_passed"] is True


def test_refusal_and_noncompleted_response_fail_explicitly() -> None:
    refusal = {
        "status": "completed",
        "output": [{"type": "message", "content": [{"type": "refusal"}]}],
    }
    incomplete = {"status": "incomplete", "output": []}

    with pytest.raises(ExperimentError, match="refusal"):
        generate("test-key", lambda request, timeout: StubResponse(refusal))
    with pytest.raises(ExperimentError, match="did not complete"):
        generate("test-key", lambda request, timeout: StubResponse(incomplete))


def test_malformed_response_json_and_output_fail_safely() -> None:
    malformed_output = {"status": "completed", "output": [{"type": "message", "content": "bad"}]}

    with pytest.raises(ExperimentError, match="invalid JSON"):
        generate("test-key", lambda request, timeout: RawResponse(b"not json"))
    with pytest.raises(ExperimentError, match="invalid response envelope"):
        generate("test-key", lambda request, timeout: StubResponse(malformed_output))


def test_invalid_shape_and_http_error_do_not_retry() -> None:
    calls = 0

    def transport(request, timeout):
        nonlocal calls
        calls += 1
        return StubResponse({}, 500)

    with pytest.raises(ExperimentError, match="HTTP status 500"):
        generate("test-key", transport)
    assert calls == 1


def test_redirects_are_rejected_without_a_fallback() -> None:
    calls = 0

    def transport(request, timeout):
        nonlocal calls
        calls += 1
        return StubResponse({}, 302)

    assert _RejectRedirects().redirect_request(Request(API_URL)) is None
    with pytest.raises(ExperimentError, match="HTTP status 302"):
        generate("test-key", transport)
    assert calls == 1


def test_syntax_check_never_executes_generated_code(tmp_path: Path) -> None:
    marker = tmp_path / "executed"
    code = f"import pathlib\ndef choose_job(jobs, now):\n    {marker!r}.write_text('bad')\n    return None\n"

    assert syntax_check(code) is False
    assert not marker.exists()


def test_syntax_check_requires_the_exact_experiment_function_shape() -> None:
    assert syntax_check("def choose_job(jobs, now, *, required):\n    return None\n") is False
    assert syntax_check("def choose_job(jobs, now, *extra):\n    return None\n") is False
    assert (
        syntax_check(
            "def choose_job(jobs, now):\n    def helper():\n        return None\n    return None\n"
        )
        is False
    )
    assert syntax_check("x = 1\ndef choose_job(jobs, now):\n    return None\n") is False
    assert syntax_check("'description'\ndef choose_job(jobs, now):\n    return None\n") is False


def test_reads_only_plain_dotenv_keys_without_shell_evaluation(tmp_path: Path, caplog) -> None:
    env_file = tmp_path / "experiment.env"
    env_file.write_text("export OPENAI_API_KEY='quoted-key'\nopenai_api_key=$(not-run)\n")

    assert read_env_key(env_file) == "quoted-key"
    assert "quoted-key" not in caplog.text


def test_reads_lowercase_dotenv_key_and_rejects_missing_key(tmp_path: Path) -> None:
    env_file = tmp_path / "experiment.env"
    env_file.write_text('openai_api_key = "lower-key"\n')

    assert read_env_key(env_file) == "lower-key"
    env_file.write_text("OTHER=value\n")
    with pytest.raises(ExperimentError, match="does not contain"):
        read_env_key(env_file)


def test_hidden_prompt_failure_cannot_fall_back_to_echoed_input(monkeypatch) -> None:
    monkeypatch.setattr(experiment.sys.stdin, "isatty", lambda: True)

    def warn_and_fail(prompt: str) -> str:
        warnings.warn("echo fallback", getpass.GetPassWarning)
        return "should-not-return"

    monkeypatch.setattr(experiment.getpass, "getpass", warn_and_fail)
    with pytest.raises(ExperimentError, match="could not read hidden"):
        _read_prompt_key()


def test_prepare_only_writes_request_without_reading_a_key_or_generating(
    tmp_path: Path, monkeypatch
) -> None:
    class RejectEnvironment:
        def get(self, key: str, default: str | None = None) -> str:
            raise AssertionError("prepare-only must not read the environment")

    class RejectOS:
        environ = RejectEnvironment()

    def forbidden(*args, **kwargs):
        raise AssertionError("prepare-only must not read a key or generate")

    monkeypatch.setattr(experiment, "os", RejectOS())
    monkeypatch.setattr(experiment, "read_env_key", forbidden)
    monkeypatch.setattr(experiment, "_read_prompt_key", forbidden)
    monkeypatch.setattr(experiment, "generate", forbidden)

    assert experiment.main(["--prepare-only", "--output-dir", str(tmp_path)]) == 0

    artifacts = list(tmp_path.glob("candidate-*.json"))
    assert len(artifacts) == 1
    assert json.loads(artifacts[0].read_text()) == {
        "experiment_only": True,
        "request": build_request(),
    }


def test_main_returns_one_and_logs_generation_failure(tmp_path: Path, monkeypatch, caplog) -> None:
    def fail_generation(api_key: str) -> dict:
        assert api_key == "dummy-key"
        raise ExperimentError("dummy generation failure")

    monkeypatch.setattr(experiment, "read_env_key", lambda path: "dummy-key")
    monkeypatch.setattr(experiment, "generate", fail_generation)

    assert experiment.main(["--env-file", str(tmp_path / "dummy.env")]) == 1
    assert "Candidate generation experiment failed: dummy generation failure" in caplog.text


def test_main_returns_one_and_logs_artifact_write_failure(
    tmp_path: Path, monkeypatch, caplog
) -> None:
    monkeypatch.setattr(experiment, "read_env_key", lambda path: "dummy-key")
    monkeypatch.setattr(
        experiment,
        "generate",
        lambda api_key: {"syntax_check_passed": True},
    )

    def fail_write(output_dir: Path, artifact: dict) -> Path:
        raise OSError("dummy write failure")

    monkeypatch.setattr(experiment, "write_artifact", fail_write)

    assert experiment.main(["--env-file", str(tmp_path / "dummy.env")]) == 1
    assert "Candidate generation experiment could not write its artifact" in caplog.text
