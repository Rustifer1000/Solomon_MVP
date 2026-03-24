from __future__ import annotations

from runtime.contracts import CandidateTurn
from runtime.plugins.base import PluginRuntime
from runtime.plugins.divorce_policy import apply_case_policy, build_case_flag_templates
from runtime.plugins.divorce_shared import PACKAGE_ELEMENT_LABELS, build_base_assessment, qualify_case_shared
from runtime.state import merge_flag_templates

PLUGIN_TYPE = "divorce"
DIVORCE_EVALUATOR_HELPER_POLICY = {
    "descriptor_id": "divorce_evaluator_helpers_v0",
    "fairness_flag_types": ["fairness_breakdown"],
    "fairness_terms": [
        "fairness",
        "balanced",
        "bias",
        "domination",
        "sidelined",
        "one-sided",
        "pressure",
        "pressured",
        "emotional",
        "heated",
        "retaliation",
        "coercive",
        "coercion",
        "unsafe",
    ],
    "fairness_issue_terms": [
        "fairness and meaningful parenting role",
        "fairness_and_parent_role",
    ],
    "fairness_attention_tags": ["fairness_sensitive"],
}


def qualify_case(case_bundle: dict) -> dict:
    return qualify_case_shared(case_bundle)


def assess_state(state: dict) -> dict:
    policy_descriptor = state["meta"].get("plugin_policy_descriptor")
    base_assessment = build_base_assessment(state)
    return apply_case_policy(policy_descriptor, base_assessment)


def sync_flags_for_turn(state: dict, turn: CandidateTurn) -> None:
    policy_descriptor = state["meta"].get("plugin_policy_descriptor")
    merge_flag_templates(state, build_case_flag_templates(policy_descriptor, state, turn))


class DivorcePluginRuntime(PluginRuntime):
    plugin_type = PLUGIN_TYPE

    def qualify_case(self, case_bundle: dict) -> dict:
        return qualify_case(case_bundle)

    def assess_state(self, state: dict) -> dict:
        return assess_state(state)

    def sync_flags_for_turn(self, state: dict, turn: CandidateTurn) -> None:
        sync_flags_for_turn(state, turn)

    def package_element_labels(self) -> dict[str, str]:
        return dict(PACKAGE_ELEMENT_LABELS)

    def evaluator_helper_policy(self) -> dict | None:
        return dict(DIVORCE_EVALUATOR_HELPER_POLICY)


DIVORCE_PLUGIN_RUNTIME = DivorcePluginRuntime()
