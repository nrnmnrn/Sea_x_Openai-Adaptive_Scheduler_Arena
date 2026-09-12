"""Internal, side-effect-free assembly for existing-Skill comparison inputs."""

from __future__ import annotations

import math
from collections.abc import Collection, Iterable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any


class ExistingSkillAdaptationValidationError(ValueError):
    """Comparison inputs cannot safely represent one completed A/B result."""

    def __init__(self, reason: str, message: str):
        super().__init__(message)
        self.reason = reason


@dataclass(frozen=True)
class ExistingSkillComparison:
    """An immutable, caller-order-preserving existing-Skill comparison."""

    run_id: str
    workload_window_id: str
    adaptation_id: str
    trigger: Mapping[str, Any]
    baseline: Mapping[str, Any]
    expected_skill_ids: tuple[str, ...]
    evaluations: tuple[Mapping[str, Any], ...]


EVALUATION_RESULT_FIELDS = (
    "subject_id",
    "subject_kind",
    "baseline_metrics",
    "evaluated_metrics",
    "evaluation_window",
    "gate_passed",
    "regressions",
    "contract_validation",
    "sandbox_status",
    "failure_reason",
    "critic_feedback",
)


def _freeze(value: Any, path: str) -> Any:
    """Copy only recursively JSON-shaped values into immutable containers."""

    if isinstance(value, Mapping):
        frozen: dict[str, Any] = {}
        for key, item in value.items():
            if type(key) is not str:
                raise ExistingSkillAdaptationValidationError(
                    "invalid_json_value", f"{path} must use string keys"
                )
            frozen[key] = _freeze(item, f"{path}.{key}")
        return MappingProxyType(frozen)
    if type(value) in (list, tuple):
        return tuple(_freeze(item, f"{path}[{index}]") for index, item in enumerate(value))
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is float and math.isfinite(value):
        return value
    raise ExistingSkillAdaptationValidationError(
        "invalid_json_value", f"{path} contains a non-JSON value"
    )


def _non_empty_text(value: Any, reason: str, message: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ExistingSkillAdaptationValidationError(reason, message)
    return value


def _comparison_identity(
    trigger: Mapping[str, Any] | None,
) -> tuple[str, str, str, Mapping[str, Any]]:
    if not isinstance(trigger, Mapping):
        raise ExistingSkillAdaptationValidationError(
            "missing_trigger", "A TriggerResult is required before assembling a comparison"
        )
    if trigger.get("triggered") is not True:
        raise ExistingSkillAdaptationValidationError(
            "trigger_not_approved", "Comparison requires a triggered TriggerResult"
        )
    _non_empty_text(
        trigger.get("reason"),
        "invalid_trigger_reason",
        "TriggerResult reason must be a non-empty string",
    )

    run_id = _non_empty_text(
        trigger.get("run_id"),
        "invalid_run_id",
        "TriggerResult run_id must be a non-empty string",
    )
    window = trigger.get("workload_window")
    if not isinstance(window, Mapping):
        raise ExistingSkillAdaptationValidationError(
            "missing_workload_window", "TriggerResult workload_window is required"
        )
    window_id = _non_empty_text(
        window.get("id"),
        "invalid_workload_window_id",
        "TriggerResult workload_window.id must be a non-empty string",
    )
    for field in ("start", "end"):
        value = window.get(field)
        if type(value) not in (int, float) or (type(value) is float and not math.isfinite(value)):
            raise ExistingSkillAdaptationValidationError(
                "invalid_workload_window_time",
                f"TriggerResult workload_window.{field} must be a finite number",
            )
    adaptation_id = _non_empty_text(
        trigger.get("adaptation_id"),
        "invalid_adaptation_id",
        "TriggerResult adaptation_id must be a non-empty string",
    )
    return run_id, window_id, adaptation_id, window


def _expected_ids(expected_skill_ids: Iterable[str]) -> tuple[str, ...]:
    if isinstance(expected_skill_ids, (str, bytes)):
        raise ExistingSkillAdaptationValidationError(
            "invalid_expected_skill_ids", "Expected Skill IDs must be a collection of strings"
        )
    try:
        skill_ids = tuple(expected_skill_ids)
    except TypeError as error:
        raise ExistingSkillAdaptationValidationError(
            "invalid_expected_skill_ids", "Expected Skill IDs must be an iterable of strings"
        ) from error
    if not skill_ids:
        raise ExistingSkillAdaptationValidationError(
            "missing_expected_skill_ids", "At least one verified Skill ID is required"
        )

    seen: set[str] = set()
    for skill_id in skill_ids:
        _non_empty_text(
            skill_id, "invalid_skill_id", "Expected Skill IDs must be non-empty strings"
        )
        if skill_id in seen:
            raise ExistingSkillAdaptationValidationError(
                "duplicate_expected_skill_id", f"Expected Skill ID is duplicated: {skill_id}"
            )
        seen.add(skill_id)
    return skill_ids


def _validated_evaluations(
    evaluations: Iterable[Mapping[str, Any]],
    expected_skill_ids: tuple[str, ...],
    baseline: Mapping[str, Any],
    workload_window: Mapping[str, Any],
) -> tuple[Mapping[str, Any], ...]:
    if isinstance(evaluations, (str, bytes, Mapping)):
        raise ExistingSkillAdaptationValidationError(
            "invalid_evaluations", "Evaluation results must be a collection of objects"
        )
    try:
        supplied = tuple(evaluations)
    except TypeError as error:
        raise ExistingSkillAdaptationValidationError(
            "invalid_evaluations", "Evaluation results must be iterable"
        ) from error

    expected = set(expected_skill_ids)
    received: set[str] = set()
    copies: list[Mapping[str, Any]] = []
    for evaluation in supplied:
        if not isinstance(evaluation, Mapping):
            raise ExistingSkillAdaptationValidationError(
                "invalid_evaluation", "Each EvaluationResult must be an object"
            )
        missing_fields = [field for field in EVALUATION_RESULT_FIELDS if field not in evaluation]
        if missing_fields:
            raise ExistingSkillAdaptationValidationError(
                "missing_evaluation_field",
                f"EvaluationResult is missing required field: {missing_fields[0]}",
            )
        if evaluation.get("subject_kind") != "skill":
            raise ExistingSkillAdaptationValidationError(
                "non_skill_subject", "EvaluationResult subject_kind must be 'skill'"
            )
        subject_id = _non_empty_text(
            evaluation.get("subject_id"),
            "invalid_subject_id",
            "EvaluationResult subject_id must be a non-empty string",
        )
        if subject_id not in expected:
            raise ExistingSkillAdaptationValidationError(
                "unknown_skill_id",
                f"EvaluationResult references an unexpected Skill ID: {subject_id}",
            )
        if subject_id in received:
            raise ExistingSkillAdaptationValidationError(
                "duplicate_skill_id", f"EvaluationResult is duplicated for Skill ID: {subject_id}"
            )
        if not isinstance(evaluation["baseline_metrics"], Mapping):
            raise ExistingSkillAdaptationValidationError(
                "invalid_baseline_metrics", "EvaluationResult baseline_metrics must be an object"
            )
        if evaluation["baseline_metrics"] != baseline:
            raise ExistingSkillAdaptationValidationError(
                "baseline_mismatch",
                "EvaluationResult baseline_metrics must match the supplied baseline",
            )
        for field in ("evaluated_metrics", "evaluation_window", "contract_validation"):
            if not isinstance(evaluation[field], Mapping):
                raise ExistingSkillAdaptationValidationError(
                    "invalid_evaluation_field", f"EvaluationResult {field} must be an object"
                )
        if evaluation["evaluation_window"] != workload_window:
            raise ExistingSkillAdaptationValidationError(
                "evaluation_window_mismatch",
                "EvaluationResult evaluation_window must match TriggerResult workload_window",
            )
        if type(evaluation["gate_passed"]) is not bool:
            raise ExistingSkillAdaptationValidationError(
                "invalid_gate_passed", "EvaluationResult gate_passed must be a boolean"
            )
        regressions = evaluation["regressions"]
        if not isinstance(regressions, Collection) or isinstance(regressions, (str, bytes)):
            raise ExistingSkillAdaptationValidationError(
                "invalid_regressions",
                "EvaluationResult regressions must be a non-string collection",
            )
        _non_empty_text(
            evaluation["sandbox_status"],
            "invalid_sandbox_status",
            "EvaluationResult sandbox_status must be a non-empty string",
        )
        for field in ("failure_reason", "critic_feedback"):
            if evaluation[field] is not None and not isinstance(evaluation[field], str):
                raise ExistingSkillAdaptationValidationError(
                    "invalid_evaluation_field", f"EvaluationResult {field} must be a string or null"
                )
        received.add(subject_id)
        copies.append(dict(evaluation))

    missing = [skill_id for skill_id in expected_skill_ids if skill_id not in received]
    if missing:
        raise ExistingSkillAdaptationValidationError(
            "missing_skill_id", f"EvaluationResult is missing for Skill ID: {missing[0]}"
        )
    return tuple(copies)


class ExistingSkillComparisonAssembler:
    """Keeps only immutable completed comparisons for supplied adaptation identities."""

    def __init__(self) -> None:
        self._by_key: dict[tuple[str, str], ExistingSkillComparison] = {}
        self._key_by_adaptation_id: dict[str, tuple[str, str]] = {}

    def assemble(
        self,
        trigger: Mapping[str, Any] | None,
        baseline: Mapping[str, Any] | None,
        expected_skill_ids: Iterable[str],
        evaluations: Iterable[Mapping[str, Any]],
    ) -> ExistingSkillComparison:
        """Collect complete existing-Skill results without interpreting their outcomes."""

        run_id, window_id, adaptation_id, workload_window = _comparison_identity(trigger)
        key = (run_id, window_id)
        existing = self._by_key.get(key)
        if existing is not None:
            if existing.adaptation_id != adaptation_id:
                raise ExistingSkillAdaptationValidationError(
                    "conflicting_adaptation_id",
                    (
                        "A different adaptation_id is already associated with this run "
                        "and workload window"
                    ),
                )
            return existing
        prior_key = self._key_by_adaptation_id.get(adaptation_id)
        if prior_key is not None and prior_key != key:
            raise ExistingSkillAdaptationValidationError(
                "adaptation_id_reused",
                "This adaptation_id is already associated with another run or workload window",
            )
        if not isinstance(baseline, Mapping):
            raise ExistingSkillAdaptationValidationError(
                "missing_baseline", "A baseline metrics object is required"
            )
        skill_ids = _expected_ids(expected_skill_ids)
        evaluation_copies = _validated_evaluations(
            evaluations, skill_ids, baseline, workload_window
        )

        comparison = ExistingSkillComparison(
            run_id=run_id,
            workload_window_id=window_id,
            adaptation_id=adaptation_id,
            trigger=_freeze(trigger, "trigger"),
            baseline=_freeze(baseline, "baseline"),
            expected_skill_ids=skill_ids,
            evaluations=_freeze(evaluation_copies, "evaluations"),
        )
        self._by_key[key] = comparison
        self._key_by_adaptation_id[adaptation_id] = key
        return comparison
