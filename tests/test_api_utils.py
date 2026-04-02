"""
tests.test_api_utils
====================
Unit tests for the cached_create wrapper and per-engine enforcement.

Two wrapper behaviour tests
---------------------------
1. test_string_system_prompt_wrapped_with_cache_control
   Plain string → converted to list with cache_control=ephemeral.

2. test_list_system_prompt_passed_through_unchanged
   Already-structured list → forwarded to messages.create as-is.

Per-engine representative tests (highest-risk paths)
-----------------------------------------------------
Each test verifies that the engine's main entry point routes through
cached_create rather than calling messages.create directly.  They mock
cached_create at the module level so no real API key is required.

Agents tested:
  - safety_monitor.generate_safety_monitor_result  (veto authority)
  - perception_agent.generate_perception_agent_result  (deep perception)
  - option_generator.generate_option_pool  (brainstorm pass)
  - domain_reasoner.generate_domain_analysis  (qualification + veto)
  - lm_engine.generate_lm_assistant_turn  (main synthesis turn)
"""

from __future__ import annotations

import json
import unittest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Wrapper unit tests
# ---------------------------------------------------------------------------

class TestCachedCreate(unittest.TestCase):
    """Unit tests for the cached_create wrapper in api_utils."""

    def setUp(self):
        from runtime.engine.api_utils import cached_create
        self.cached_create = cached_create
        self.client = MagicMock()

    def test_string_system_prompt_wrapped_with_cache_control(self):
        """Plain string system prompt is converted to a list with cache_control."""
        self.cached_create(
            self.client,
            system="You are a mediator.",
            model="claude-sonnet-4-5",
            max_tokens=100,
            messages=[{"role": "user", "content": "hello"}],
        )
        _, kwargs = self.client.messages.create.call_args
        system = kwargs["system"]
        self.assertIsInstance(system, list)
        self.assertEqual(len(system), 1)
        self.assertEqual(system[0]["type"], "text")
        self.assertEqual(system[0]["text"], "You are a mediator.")
        self.assertEqual(system[0]["cache_control"], {"type": "ephemeral"})

    def test_list_system_prompt_passed_through_unchanged(self):
        """Already-structured list system prompt is passed through unchanged."""
        structured = [
            {"type": "text", "text": "You are a mediator.", "cache_control": {"type": "ephemeral"}}
        ]
        self.cached_create(
            self.client,
            system=structured,
            model="claude-sonnet-4-5",
            max_tokens=100,
            messages=[{"role": "user", "content": "hello"}],
        )
        _, kwargs = self.client.messages.create.call_args
        self.assertIs(kwargs["system"], structured)

    def test_kwargs_forwarded_to_messages_create(self):
        """All extra kwargs are forwarded to client.messages.create."""
        messages = [{"role": "user", "content": "test"}]
        self.cached_create(
            self.client,
            system="sys",
            model="claude-sonnet-4-5",
            max_tokens=512,
            messages=messages,
        )
        _, kwargs = self.client.messages.create.call_args
        self.assertEqual(kwargs["model"], "claude-sonnet-4-5")
        self.assertEqual(kwargs["max_tokens"], 512)
        self.assertEqual(kwargs["messages"], messages)


# ---------------------------------------------------------------------------
# Per-engine representative tests
# ---------------------------------------------------------------------------

_MINIMAL_STATE = {
    "meta": {"case_id": "test-case", "session_id": "s1"},
    "phase": "info_gathering",
    "trace_buffer": [],
    "positions": {},
    "missing_info": [],
    "facts": [],
    "flags": [],
    "escalation": {"mode": "M0"},
}

_MINIMAL_PLUGIN = {
    "plugin_confidence": "low",
    "option_posture": "none",
    "active_flag_types": [],
    "issue_families": [],
    "domain": "divorce",
}

_TIMESTAMP = "2026-04-02T00:00:00Z"


def _mock_response(text: str) -> MagicMock:
    resp = MagicMock()
    resp.content = [MagicMock(text=text)]
    return resp


class TestSafetyMonitorUsesCachedCreate(unittest.TestCase):
    """safety_monitor.generate_safety_monitor_result must use cached_create."""

    @patch("runtime.engine.safety_monitor.cached_create")
    @patch("runtime.engine.safety_monitor._make_client")
    @patch("runtime.engine.safety_monitor._get_model", return_value="claude-sonnet-4-5")
    def test_routes_through_cached_create(self, _mock_model, _mock_client, mock_cached):
        from runtime.engine.safety_monitor import generate_safety_monitor_result

        payload = json.dumps({
            "compliance_pattern": {"detected": False},
            "deflection_pattern": {"detected": False},
            "discordant_signals": [],
            "veto_recommendation": None,
            "veto_reason": None,
            "monitor_confidence": "low",
            "monitor_notes": "no patterns detected",
        })
        mock_cached.return_value = _mock_response(payload)

        # turn_index=3 — skips the insufficient-history guard
        history = [
            {"role": "client", "turn_index": 1, "message_text": "Hi", "message_summary": "Hi"},
            {"role": "assistant", "turn_index": 2, "message_summary": "Hello"},
        ]
        result = generate_safety_monitor_result(
            turn_index=3,
            timestamp=_TIMESTAMP,
            state=_MINIMAL_STATE,
            interaction_history=history,
        )

        self.assertTrue(mock_cached.called, "cached_create was not called")
        _, kwargs = mock_cached.call_args
        self.assertIn("system", kwargs)
        self.assertIsInstance(kwargs["system"], str)


class TestPerceptionAgentUsesCachedCreate(unittest.TestCase):
    """perception_agent.generate_perception_agent_result must use cached_create."""

    @patch("runtime.engine.perception_agent.cached_create")
    @patch("runtime.engine.perception_agent._make_client")
    @patch("runtime.engine.perception_agent._get_model", return_value="claude-sonnet-4-5")
    def test_routes_through_cached_create(self, _mock_model, _mock_client, mock_cached):
        from runtime.engine.perception_agent import generate_perception_agent_result

        payload = json.dumps({
            "party_a": {
                "emotional_state": "calm",
                "emotional_trajectory": "stable",
                "engagement_quality": "genuine",
                "communication_style": "direct",
                "inferred_interests": [],
                "inferred_concerns": [],
                "unsaid_signals": [],
                "relational_posture": "cooperative",
            },
            "party_b": {
                "emotional_state": "calm",
                "emotional_trajectory": "stable",
                "engagement_quality": "genuine",
                "communication_style": "direct",
                "inferred_interests": [],
                "inferred_concerns": [],
                "unsaid_signals": [],
                "relational_posture": "cooperative",
            },
            "relational_dynamic": "cooperative",
            "dynamic_trajectory": "stable",
            "perception_signals": [],
            "scaffold_divergence": None,
            "perception_notes": [],
            "veto_signals": [],
            "confidence": "low",
        })
        mock_cached.return_value = _mock_response(payload)

        scaffold = MagicMock()
        scaffold.party_a = MagicMock(
            emotional_state="neutral", relational_posture="cooperative", risk_signals=[]
        )
        scaffold.party_b = MagicMock(
            emotional_state="neutral", relational_posture="cooperative", risk_signals=[]
        )
        scaffold.relational_dynamic = "cooperative"
        scaffold.perception_confidence = "low"
        scaffold.perception_notes = []

        history = [
            {"role": "client", "turn_index": 1, "message_text": "Hi", "message_summary": "Hi"},
            {"role": "assistant", "turn_index": 2, "message_summary": "Hello"},
        ]
        result = generate_perception_agent_result(
            turn_index=3,
            timestamp=_TIMESTAMP,
            state=_MINIMAL_STATE,
            scaffold_perception=scaffold,
            interaction_history=history,
        )

        self.assertTrue(mock_cached.called, "cached_create was not called")
        _, kwargs = mock_cached.call_args
        self.assertIn("system", kwargs)
        self.assertIsInstance(kwargs["system"], str)


class TestOptionGeneratorUsesCachedCreate(unittest.TestCase):
    """option_generator.generate_option_pool must use cached_create."""

    @patch("runtime.engine.option_generator.cached_create")
    @patch("runtime.engine.option_generator._make_client")
    @patch("runtime.engine.option_generator._get_model", return_value="claude-sonnet-4-5")
    def test_routes_through_cached_create(self, _mock_model, _mock_client, mock_cached):
        from runtime.engine.option_generator import generate_option_pool

        payload = json.dumps({
            "brainstormer_candidates": [
                {
                    "candidate_id": "opt-gen-001",
                    "label": "Tiered notice system",
                    "rationale": "Addresses timing concerns.",
                    "party_interest_alignment": {"party_a": "predictability", "party_b": "flexibility"},
                    "related_issues": [],
                }
            ]
        })
        mock_cached.return_value = _mock_response(payload)

        party_state = {
            "party_a": {"accumulated_interests": [], "relational_posture_progression": [], "current_emotional_state": "neutral", "current_relational_posture": "cooperative"},
            "party_b": {"accumulated_interests": [], "relational_posture_progression": [], "current_emotional_state": "neutral", "current_relational_posture": "cooperative"},
            "cross_party": {"current_relational_dynamic": "cooperative"},
        }

        result = generate_option_pool(
            turn_index=5,
            timestamp=_TIMESTAMP,
            state=_MINIMAL_STATE,
            party_state=party_state,
            plugin_assessment=_MINIMAL_PLUGIN,
            session_history=[],
        )

        self.assertTrue(mock_cached.called, "cached_create was not called")
        _, kwargs = mock_cached.call_args
        self.assertIn("system", kwargs)
        self.assertIsInstance(kwargs["system"], str)


class TestDomainReasonerUsesCachedCreate(unittest.TestCase):
    """domain_reasoner.generate_domain_analysis must use cached_create."""

    @patch("runtime.engine.domain_reasoner.cached_create")
    @patch("runtime.engine.domain_reasoner._make_client")
    @patch("runtime.engine.domain_reasoner._get_model", return_value="claude-sonnet-4-5")
    def test_routes_through_cached_create(self, _mock_model, _mock_client, mock_cached):
        from runtime.engine.domain_reasoner import generate_domain_analysis

        payload = json.dumps({
            "option_readiness": "deferred",
            "readiness_rationale": "Insufficient information.",
            "safety_veto_applied": False,
            "safety_veto_reason": None,
            "qualified_candidates": [],
            "blocking_constraints": [],
            "material_gaps": [],
            "domain_confidence": "low",
            "domain_notes": "Early session.",
        })
        mock_cached.return_value = _mock_response(payload)

        result = generate_domain_analysis(
            turn_index=3,
            timestamp=_TIMESTAMP,
            state=_MINIMAL_STATE,
            party_state=None,
            plugin_assessment=_MINIMAL_PLUGIN,
            session_history=[],
        )

        self.assertTrue(mock_cached.called, "cached_create was not called")
        _, kwargs = mock_cached.call_args
        self.assertIn("system", kwargs)
        self.assertIsInstance(kwargs["system"], str)


class TestLmEngineUsesCachedCreate(unittest.TestCase):
    """lm_engine.generate_lm_assistant_turn must use cached_create for the main synthesis call."""

    @patch("runtime.engine.lm_engine.cached_create")
    @patch("runtime.engine.lm_engine._make_client")
    @patch("runtime.engine.lm_engine._get_model", return_value="claude-sonnet-4-5")
    @patch("runtime.engine.lm_engine.generate_perception_agent_result")
    @patch("runtime.engine.lm_engine.generate_domain_analysis")
    @patch("runtime.engine.lm_engine.build_perception_context")
    def test_routes_through_cached_create(
        self,
        mock_build_perception,
        mock_domain,
        mock_perception_agent,
        _mock_model,
        _mock_client,
        mock_cached,
    ):
        from runtime.engine.lm_engine import generate_lm_assistant_turn

        # Scaffold perception mock
        scaffold = MagicMock()
        scaffold.party_a = MagicMock(
            emotional_state="neutral", relational_posture="cooperative", risk_signals=[]
        )
        scaffold.party_b = MagicMock(
            emotional_state="neutral", relational_posture="cooperative", risk_signals=[]
        )
        scaffold.relational_dynamic = ""
        scaffold.perception_confidence = "low"
        scaffold.perception_notes = []
        mock_build_perception.return_value = scaffold

        mock_perception_agent.return_value = {"_null_result": True}
        mock_domain.return_value = {
            "option_readiness": "deferred",
            "readiness_rationale": "test",
            "safety_veto_applied": False,
            "safety_veto_reason": None,
            "qualified_candidates": [],
            "blocking_constraints": [],
            "material_gaps": [],
            "domain_confidence": "low",
            "domain_notes": "test",
        }

        lm_json = json.dumps({
            "perception": {"party_a": {}, "party_b": {}, "relational_dynamic": ""},
            "domain_analysis": {"material_gaps": [], "key_constraints": []},
            "option_scan": {"qualified_options": [], "premature_option_work": False},
            "safety_check": {
                "escalation_needed": False,
                "candidate_mode": "M0",
                "candidate_category": "E0",
                "signals": [],
                "notes": "",
            },
            "response": {
                "phase": "info_gathering",
                "message_summary": "Welcome.",
                "message_text": "Welcome to the session.",
                "confidence_note": "low",
            },
        })
        mock_cached.return_value = _mock_response(lm_json)

        result = generate_lm_assistant_turn(
            turn_index=1,
            timestamp=_TIMESTAMP,
            state=_MINIMAL_STATE,
            plugin_assessment=_MINIMAL_PLUGIN,
        )

        self.assertTrue(mock_cached.called, "cached_create was not called")
        _, kwargs = mock_cached.call_args
        self.assertIn("system", kwargs)
        self.assertIsInstance(kwargs["system"], str)


if __name__ == "__main__":
    unittest.main()
