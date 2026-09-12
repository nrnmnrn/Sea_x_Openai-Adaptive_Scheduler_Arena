import pytest

from existing_skill_adaptation import (
    EVALUATION_RESULT_FIELDS,
    ExistingSkillAdaptationValidationError,
    ExistingSkillComparisonAssembler,
)


def trigger(**overrides):
    value = {
        "triggered": True,
        "reason": "expired jobs increased",
        "run_id": "run-1",
        "workload_window": {"id": "window-1", "start": 0, "end": 10},
        "adaptation_id": "adaptation-1",
    }
    value.update(overrides)
    return value


def baseline(**overrides):
    value = {"completed": 3, "expired": 2, "p95_latency": None}
    value.update(overrides)
    return value


def evaluation(skill_id, **overrides):
    value = {
        "subject_id": skill_id,
        "subject_kind": "skill",
        "baseline_metrics": baseline(),
        "evaluated_metrics": {"completed": 4, "expired": 1, "p95_latency": None},
        "evaluation_window": {"id": "window-1", "start": 0, "end": 10},
        "gate_passed": False,
        "regressions": [],
        "contract_validation": {"valid": True},
        "sandbox_status": "completed",
        "failure_reason": None,
        "critic_feedback": None,
    }
    value.update(overrides)
    return value


def assemble(**overrides):
    values = {
        "trigger": trigger(),
        "baseline": baseline(),
        "expected_skill_ids": ["fifo", "edf"],
        "evaluations": [evaluation("fifo"), evaluation("edf")],
    }
    values.update(overrides)
    return ExistingSkillComparisonAssembler().assemble(**values)


def test_assembles_complete_comparison_in_caller_evaluation_order():
    result = assemble(evaluations=[evaluation("edf"), evaluation("fifo")])

    assert result.run_id == "run-1"
    assert result.workload_window_id == "window-1"
    assert result.expected_skill_ids == ("fifo", "edf")
    assert [item["subject_id"] for item in result.evaluations] == ["edf", "fifo"]


def test_repeated_identity_reuses_first_immutable_result():
    assembler = ExistingSkillComparisonAssembler()
    first = assembler.assemble(
        trigger(), baseline(), ["fifo", "edf"], [evaluation("fifo"), evaluation("edf")]
    )
    second = assembler.assemble(
        trigger(), baseline(), ["fifo", "edf"], [evaluation("fifo"), evaluation("edf")]
    )

    assert second is first
    with pytest.raises(TypeError):
        first.baseline["expired"] = 99
    with pytest.raises(TypeError):
        first.trigger["workload_window"]["id"] = "changed"


def test_repeated_identity_reuses_first_result_without_reprocessing_replay_inputs():
    assembler = ExistingSkillComparisonAssembler()
    first = assembler.assemble(
        trigger(), baseline(), ["fifo", "edf"], [evaluation("fifo"), evaluation("edf")]
    )

    replay = assembler.assemble(trigger(), None, [], [])

    assert replay is first


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"adaptation_id": "adaptation-2"}, "conflicting_adaptation_id"),
        (
            {
                "run_id": "run-2",
                "workload_window": {"id": "window-2", "start": 10, "end": 20},
            },
            "adaptation_id_reused",
        ),
    ],
)
def test_conflicting_adaptation_identities_are_rejected(changes, reason):
    assembler = ExistingSkillComparisonAssembler()
    assembler.assemble(
        trigger(), baseline(), ["fifo", "edf"], [evaluation("fifo"), evaluation("edf")]
    )

    with pytest.raises(ExistingSkillAdaptationValidationError) as error:
        assembler.assemble(
            trigger(**changes),
            baseline(),
            ["fifo", "edf"],
            [evaluation("fifo"), evaluation("edf")],
        )
    assert error.value.reason == reason


@pytest.mark.parametrize(
    ("expected_ids", "results", "reason"),
    [
        (["fifo", "edf"], [evaluation("fifo")], "missing_skill_id"),
        (
            ["fifo", "edf"],
            [evaluation("fifo"), evaluation("fifo"), evaluation("edf")],
            "duplicate_skill_id",
        ),
        (["fifo", "edf"], [evaluation("fifo"), evaluation("sjf")], "unknown_skill_id"),
        (["fifo", "fifo"], [evaluation("fifo")], "duplicate_expected_skill_id"),
    ],
)
def test_result_completeness_and_expected_id_errors_are_rejected(expected_ids, results, reason):
    with pytest.raises(ExistingSkillAdaptationValidationError) as error:
        assemble(expected_skill_ids=expected_ids, evaluations=results)
    assert error.value.reason == reason


@pytest.mark.parametrize(
    ("value", "reason"),
    [(None, "missing_trigger"), (trigger(triggered=False), "trigger_not_approved")],
)
def test_missing_or_untriggered_trigger_cannot_start_comparison(value, reason):
    with pytest.raises(ExistingSkillAdaptationValidationError) as error:
        assemble(trigger=value)
    assert error.value.reason == reason


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"reason": ""}, "invalid_trigger_reason"),
        ({"workload_window": {"id": "window-1", "start": 0}}, "invalid_workload_window_time"),
        (
            {"workload_window": {"id": "window-1", "start": float("inf"), "end": 10}},
            "invalid_workload_window_time",
        ),
    ],
)
def test_trigger_requires_structural_evidence_without_interpreting_it(changes, reason):
    with pytest.raises(ExistingSkillAdaptationValidationError) as error:
        assemble(trigger=trigger(**changes))
    assert error.value.reason == reason


def test_missing_baseline_and_result_baseline_mismatch_are_rejected():
    with pytest.raises(ExistingSkillAdaptationValidationError) as missing:
        assemble(baseline=None)
    assert missing.value.reason == "missing_baseline"

    with pytest.raises(ExistingSkillAdaptationValidationError) as mismatch:
        assemble(
            evaluations=[evaluation("fifo"), evaluation("edf", baseline_metrics={"expired": 0})]
        )
    assert mismatch.value.reason == "baseline_mismatch"


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"subject_kind": "candidate"}, "non_skill_subject"),
        ({"subject_id": ""}, "invalid_subject_id"),
    ],
)
def test_wrong_subject_kind_or_id_is_rejected(changes, reason):
    with pytest.raises(ExistingSkillAdaptationValidationError) as error:
        assemble(evaluations=[evaluation("fifo", **changes), evaluation("edf")])
    assert error.value.reason == reason


@pytest.mark.parametrize("field", EVALUATION_RESULT_FIELDS)
def test_each_contract_minimum_evaluation_field_is_required(field):
    incomplete = evaluation("fifo")
    del incomplete[field]

    with pytest.raises(ExistingSkillAdaptationValidationError) as error:
        assemble(evaluations=[incomplete, evaluation("edf")])
    assert error.value.reason == "missing_evaluation_field"


def test_evaluations_must_share_one_evaluation_window():
    with pytest.raises(ExistingSkillAdaptationValidationError) as error:
        assemble(
            evaluations=[
                evaluation("fifo"),
                evaluation("edf", evaluation_window={"id": "other-window", "start": 0, "end": 10}),
            ]
        )
    assert error.value.reason == "evaluation_window_mismatch"


def test_evaluations_with_a_shared_wrong_window_are_rejected():
    wrong_window = {"id": "other-window", "start": 0, "end": 10}

    with pytest.raises(ExistingSkillAdaptationValidationError) as error:
        assemble(
            evaluations=[
                evaluation("fifo", evaluation_window=wrong_window),
                evaluation("edf", evaluation_window=wrong_window),
            ]
        )

    assert error.value.reason == "evaluation_window_mismatch"


def test_input_mutation_after_assembly_does_not_change_result():
    supplied_trigger = trigger()
    supplied_baseline = baseline()
    supplied_results = [evaluation("fifo"), evaluation("edf")]
    result = ExistingSkillComparisonAssembler().assemble(
        supplied_trigger, supplied_baseline, ["fifo", "edf"], supplied_results
    )

    supplied_trigger["workload_window"]["id"] = "changed"
    supplied_baseline["expired"] = 99
    supplied_results[0]["evaluated_metrics"]["expired"] = 99

    assert result.trigger["workload_window"]["id"] == "window-1"
    assert result.baseline["expired"] == 2
    assert result.evaluations[0]["evaluated_metrics"]["expired"] == 1


@pytest.mark.parametrize(
    "changes",
    [
        {"evaluated_metrics": {"nested": {"not_json"}}},
        {"evaluated_metrics": {"bad": {"set_value"}}},
    ],
)
def test_non_json_nested_values_are_rejected(changes):
    with pytest.raises(ExistingSkillAdaptationValidationError) as error:
        assemble(evaluations=[evaluation("fifo", **changes), evaluation("edf")])
    assert error.value.reason == "invalid_json_value"


def test_non_finite_json_values_are_rejected():
    supplied_baseline = {"p95_latency": float("inf")}
    with pytest.raises(ExistingSkillAdaptationValidationError) as error:
        assemble(
            baseline=supplied_baseline,
            evaluations=[
                evaluation("fifo", baseline_metrics=supplied_baseline),
                evaluation("edf", baseline_metrics=supplied_baseline),
            ],
        )
    assert error.value.reason == "invalid_json_value"


def test_gate_values_are_preserved_not_interpreted():
    result = assemble(
        evaluations=[
            evaluation("fifo", gate_passed=False, sandbox_status="unknown"),
            evaluation("edf", gate_passed=True, sandbox_status="failed"),
        ]
    )

    assert [item["gate_passed"] for item in result.evaluations] == [False, True]
    assert [item["sandbox_status"] for item in result.evaluations] == ["unknown", "failed"]
    assert not hasattr(result, "all_skills_failed")
