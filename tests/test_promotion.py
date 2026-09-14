import pytest

from promotion import PromotionValidationError, present_skill_library, validate_promotion_input


def candidate(**overrides):
    value = {
        "candidate_id": "candidate-1",
        "version": 1,
        "policy_code": "def policy(job): return job.deadline",
        "status": "passed",
        "reason": "lower expired count",
    }
    value.update(overrides)
    return value


def evaluation(**overrides):
    value = {
        "subject_id": "candidate-1",
        "subject_kind": "candidate",
        "gate_passed": True,
        "sandbox_status": "passed",
        "policy_code": "def policy(job): return job.deadline",
    }
    value.update(overrides)
    return value


def test_valid_pair_creates_candidate_skill_without_side_effects():
    original = candidate()
    result = validate_promotion_input(original, evaluation())
    assert result.skill["source"] == "candidate"
    assert result.skill["verified"] is True
    assert result.skill["uses"] == 0
    assert original["status"] == "passed"


@pytest.mark.parametrize(
    ("candidate_changes", "evaluation_changes", "reason"),
    [
        ({"status": "failed"}, {}, "candidate_not_passed"),
        ({}, {"gate_passed": False}, "gate_not_passed"),
        ({}, {"sandbox_status": "unknown"}, "sandbox_not_passed"),
        ({"candidate_id": "other"}, {}, "mismatched_subject"),
        ({}, {"policy_code": "different"}, "mismatched_code"),
    ],
)
def test_invalid_pair_is_rejected_with_reason(candidate_changes, evaluation_changes, reason):
    with pytest.raises(PromotionValidationError) as error:
        validate_promotion_input(candidate(**candidate_changes), evaluation(**evaluation_changes))
    assert error.value.reason == reason


def test_missing_or_duplicate_input_is_rejected():
    with pytest.raises(PromotionValidationError) as missing:
        validate_promotion_input(candidate(), None)
    assert missing.value.reason == "missing_evaluation"
    with pytest.raises(PromotionValidationError) as duplicate:
        validate_promotion_input(candidate(), evaluation(), existing_skill_ids=["candidate-1"])
    assert duplicate.value.reason == "duplicate_skill"


def test_validated_data_is_immutable_and_library_view_is_defensive():
    result = validate_promotion_input(candidate(), evaluation())
    with pytest.raises(TypeError):
        result.skill["uses"] = 1

    skill = {
        "id": "fifo",
        "name": "FIFO",
        "description": "first in first out",
        "code": "fifo_key",
        "source": "base",
        "verified": True,
        "uses": 2,
        "last_applied_at": 1.0,
    }
    view = present_skill_library([skill])
    view[0]["uses"] = 99
    assert skill["uses"] == 2


def test_library_view_rejects_missing_contract_fields():
    with pytest.raises(ValueError, match="missing fields"):
        present_skill_library([{"id": "incomplete"}])
