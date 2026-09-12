"""Internal S04-A validation and Skill Library presentation helpers."""

from __future__ import annotations

import copy
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

SKILL_FIELDS = (
    "id",
    "name",
    "description",
    "code",
    "source",
    "verified",
    "uses",
    "last_applied_at",
)


class PromotionValidationError(ValueError):
    """A promotion input is not safe to pass to a future register operation."""

    def __init__(self, reason: str, message: str):
        super().__init__(message)
        self.reason = reason


@dataclass(frozen=True)
class ValidatedPromotion:
    """Validated, side-effect-free promotion data for a future provider."""

    candidate: Mapping[str, Any]
    evaluation: Mapping[str, Any]
    skill: Mapping[str, Any]


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def _required_text(data: Mapping[str, Any], field: str, reason: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise PromotionValidationError(reason, f"{field} must be a non-empty string")
    return value


def validate_promotion_input(
    candidate: Mapping[str, Any] | None,
    evaluation: Mapping[str, Any] | None,
    existing_skill_ids: Iterable[str] = (),
) -> ValidatedPromotion:
    """Validate a Candidate/result pair without changing any caller-owned data."""

    if not isinstance(candidate, Mapping):
        raise PromotionValidationError("missing_candidate", "Candidate is required")
    if not isinstance(evaluation, Mapping):
        raise PromotionValidationError("missing_evaluation", "EvaluationResult is required")

    candidate_id = _required_text(candidate, "candidate_id", "invalid_candidate_id")
    if candidate_id in set(existing_skill_ids):
        raise PromotionValidationError("duplicate_skill", "Candidate is already registered")
    version = candidate.get("version")
    if isinstance(version, bool) or not isinstance(version, int) or version < 1:
        raise PromotionValidationError("invalid_version", "Candidate version must be positive")
    code = _required_text(candidate, "policy_code", "invalid_policy_code")
    if candidate.get("status") != "passed":
        raise PromotionValidationError("candidate_not_passed", "Candidate is not gate-passed")

    subject_id = evaluation.get("subject_id")
    if subject_id != candidate_id:
        raise PromotionValidationError(
            "mismatched_subject", "EvaluationResult subject does not match Candidate"
        )
    if evaluation.get("subject_kind") != "candidate":
        raise PromotionValidationError(
            "invalid_subject_kind", "EvaluationResult must describe a Candidate"
        )
    if evaluation.get("gate_passed") is not True:
        raise PromotionValidationError(
            "gate_not_passed", "EvaluationResult gate_passed must be true"
        )
    if evaluation.get("sandbox_status") != "passed":
        raise PromotionValidationError("sandbox_not_passed", "Sandbox status must be passed")
    result_code = evaluation.get("policy_code")
    if result_code is not None and result_code != code:
        raise PromotionValidationError(
            "mismatched_code", "Candidate and EvaluationResult code do not match"
        )

    candidate_copy = copy.deepcopy(dict(candidate))
    evaluation_copy = copy.deepcopy(dict(evaluation))
    skill = {
        "id": candidate_id,
        "name": candidate.get("name") or f"Candidate {candidate_id} v{version}",
        "description": candidate.get("reason", "Promoted candidate policy"),
        "code": code,
        "source": "candidate",
        "verified": True,
        "uses": 0,
        "last_applied_at": None,
    }
    return ValidatedPromotion(_freeze(candidate_copy), _freeze(evaluation_copy), _freeze(skill))


def present_skill_library(skills: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Return a defensive, contract-shaped view without adding Skill metadata."""

    presented = []
    for skill in skills:
        if not isinstance(skill, Mapping):
            raise TypeError("Skill Library entries must be objects")
        missing = [field for field in SKILL_FIELDS if field not in skill]
        if missing:
            raise ValueError(f"Skill is missing fields: {', '.join(missing)}")
        presented.append({field: copy.deepcopy(skill[field]) for field in SKILL_FIELDS})
    return presented
