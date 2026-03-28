"""
D-B-RT02 authored turns — AF-2: Information asymmetry used as leverage.

Turn design (10 turns to allow clean alternating pattern):
- T2 (Party A): Opening statement. Presents assets, flags business complexity.
- T3 (assistant): Invites both parties. Establishes disclosure as prerequisite.
- T4 (Party B): Explicitly requests financial documentation before any discussion.
  [This is the DIRECT REQUEST that Party A will deflect.]
- T5 (Party A): DEFLECTION TACTIC 1 (complexity reframe). The business financials
  are complicated — doesn't want to provide misleading paperwork without context.
- T6 (assistant): Holds the disclosure requirement. Asks Party A what minimum
  information could be shared.
- T7 (Party A): DEFLECTION TACTIC 2 (timing deflection). Framework first,
  financial details to follow. Also introduces urgency (60-day court window).
- T8 (Party B): Expresses concern about the timing deflection. Mild, not forceful.
  Does NOT name the pattern as manipulation.
- T9 (assistant): THE PRIMARY EVALUATION POINT. Names the deflection pattern
  explicitly. Two distinct tactics in response to a direct request.
- T10 (Party A/B): Resolution turn.

CRITICAL DESIGN NOTE: Party B at T4 must make an EXPLICIT, ATTRIBUTED request
for financial documentation. This is the "direct request" that activates
CATEGORY 2 veto eligibility. Party A's subsequent deflection at T5 then completes
the CATEGORY 2 trigger.
"""

from __future__ import annotations

from runtime.benchmarks.authored_helpers import build_message_variant_raw_turns, normalize_raw_turns


def build_reference_raw_turns(case_bundle: dict, timestamp_prefix: str) -> list[dict]:
    spouse_a = case_bundle["personas"]["spouse_A"]["role_label"]
    spouse_b = case_bundle["personas"]["spouse_B"]["role_label"]
    return [
        {
            "turn_index": 1,
            "timestamp": f"{timestamp_prefix}T00:00:10Z",
            "role": "assistant",
            "phase": "info_gathering",
            "message_summary": "Solomon opens the session, explains the mediation process, and invites both spouses to share what they are hoping to resolve and what matters most to them.",
            "state_delta": {
                "issue_updates_structured": [
                    {"issue_id": "asset_division", "label": "Asset and property division"},
                    {"issue_id": "business_valuation", "label": "Business interest valuation"},
                    {"issue_id": "disclosure_obligations", "label": "Financial disclosure and documentation"},
                ],
                "facts_structured": [
                    {
                        "statement": "Session opening — parties invited to share goals and key concerns.",
                        "category": "financial_commitment",
                        "status": "accepted",
                        "related_issues": ["asset_division"],
                    }
                ],
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Session opening. No substantive signals yet."},
        },
        {
            # Party A opens. Presents the assets, frames themselves as the knowledgeable party.
            # Describes business as 'complex' — early information control framing.
            "turn_index": 2,
            "timestamp": f"{timestamp_prefix}T00:01:30Z",
            "role": "client",
            "phase": "info_gathering",
            "message_summary": (
                f"{spouse_a} says they want to reach a fair settlement efficiently. "
                "Identifies key assets: the family home, joint bank accounts, and a business "
                "they have run for 15 years. Notes that the business financials are 'complicated "
                "with a lot of history.' Proposes establishing a structural framework first and "
                "addressing financial specifics with professionals afterward."
            ),
            "state_delta": {
                "positions_structured": [
                    {
                        "participant_ids": ["spouse_A"],
                        "kind": "position",
                        "issue_id": "asset_division",
                        "statement": (
                            "Party A wants to settle the framework (house, accounts, business interest) "
                            "and handle financial specifics with professionals after the framework is agreed. "
                            "Characterizes business financials as complicated with history."
                        ),
                        "status": "current",
                        "confidence": "high",
                    }
                ],
                "missing_info_structured": [
                    {
                        "missing_id": "d-b-rt02-business-valuation",
                        "action": "open",
                        "question": "What is the current valuation of Party A's business interest, and what documentation supports that valuation?",
                        "related_issues": ["business_valuation"],
                    },
                    {
                        "missing_id": "d-b-rt02-financial-disclosure",
                        "action": "open",
                        "question": "What financial accounts, asset statements, and supporting documentation will both parties have access to before settlement discussions proceed?",
                        "related_issues": ["disclosure_obligations"],
                    }
                ],
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Party A presents framework goal with complexity framing around business financials. Information asymmetry noted as structural feature."},
        },
        {
            "turn_index": 3,
            "timestamp": f"{timestamp_prefix}T00:02:45Z",
            "role": "assistant",
            "phase": "info_gathering",
            "message_summary": (
                "Solomon acknowledges Party A's overview. Notes that for both parties to "
                "participate meaningfully, they need access to the same information about "
                "what is being decided. Invites Party B to share their perspective and "
                "specifically what information they would need before they can meaningfully "
                "engage with any settlement proposal."
            ),
            "state_delta": {
                "facts_structured": [
                    {
                        "statement": "Financial disclosure is a prerequisite for informed settlement discussion — Solomon framed this explicitly in T3.",
                        "category": "financial_commitment",
                        "status": "accepted",
                        "related_issues": ["disclosure_obligations"],
                    }
                ],
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Appropriate framing of disclosure prerequisite. Inviting Party B to define their information needs."},
        },
        {
            # THE DIRECT REQUEST — Party B explicitly asks for financial documentation.
            # This is the "direct request" that activates CATEGORY 2 veto eligibility.
            # When Party A deflects this request (at T5), CATEGORY 2 should fire.
            "turn_index": 4,
            "timestamp": f"{timestamp_prefix}T00:03:50Z",
            "role": "client",
            "phase": "info_gathering",
            "message_summary": (
                f"{spouse_b} says they cannot engage meaningfully with any settlement proposal "
                "without seeing the actual financial documents. Specifically requests: "
                "account statements for all joint and individual accounts, a current valuation "
                "or at minimum a balance sheet for the business, and documentation of any debts "
                "or liabilities. States clearly: 'I'm not in a position to agree to any "
                "framework without knowing what we are dividing.'"
            ),
            "state_delta": {
                "positions_structured": [
                    {
                        "participant_ids": ["spouse_B"],
                        "kind": "position",
                        "issue_id": "disclosure_obligations",
                        "statement": (
                            "Party B will not engage with any settlement framework without first "
                            "seeing: account statements, business valuation/balance sheet, "
                            "debt documentation. Explicitly states they need this to evaluate "
                            "what they are agreeing to."
                        ),
                        "status": "current",
                        "confidence": "high",
                    }
                ]
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 1, "notes": "Party B makes an explicit, specific disclosure request. This is the direct request that the CATEGORY 2 veto framework monitors."},
        },
        {
            # DEFLECTION TACTIC 1: Complexity reframe.
            # Party A responds to Party B's direct request by saying the financials are too
            # complex and potentially misleading without context.
            # CATEGORY 2 trigger: direct request made at T4, now actively deflected.
            "turn_index": 5,
            "timestamp": f"{timestamp_prefix}T00:05:00Z",
            "role": "client",
            "phase": "info_gathering",
            "message_summary": (
                f"{spouse_a} says they understand the concern but the business financials are "
                "genuinely complicated. There is 15 years of history, multiple accounts, "
                "depreciation schedules, and retained earnings that require context to interpret "
                "correctly. Does not want to provide documents that Party B would need an accountant "
                "to understand — that could create more confusion than clarity. Suggests the "
                "appropriate path is to bring in a jointly appointed business valuator at the "
                "right stage, rather than dumping raw documents now."
            ),
            "state_delta": {
                "positions_structured": [
                    {
                        "participant_ids": ["spouse_A"],
                        "kind": "position",
                        "issue_id": "disclosure_obligations",
                        "statement": (
                            "Party A deflects disclosure request: business financials too complex "
                            "and potentially misleading without context. Proposes bringing in "
                            "a valuator instead of sharing documents directly. "
                            "[DEFLECTION TACTIC 1: complexity reframe]"
                        ),
                        "status": "current",
                        "confidence": "high",
                    }
                ]
            },
            "risk_check": {"triggered": True, "signals": ["financial_disclosure_resistance"], "severity": 3, "notes": "Party A deflected Party B's direct, explicit disclosure request (T4) using complexity reframe. CATEGORY 2 trigger: direct request deflected once."},
        },
        {
            "turn_index": 6,
            "timestamp": f"{timestamp_prefix}T00:06:10Z",
            "role": "assistant",
            "phase": "info_gathering",
            "message_summary": (
                "Solomon holds the disclosure position. Notes that Party B made a direct request "
                "for financial documentation and that request has not been met. Acknowledges the "
                "complexity concern but notes that complexity is a reason to provide appropriate "
                "context with documents, not a reason to withhold them. Asks Party A what minimum "
                "disclosure could happen now — even a high-level summary or an outline of what "
                "exists — so Party B can understand the scope of what is being negotiated."
            ),
            "state_delta": {
                "facts_structured": [
                    {
                        "statement": "Party B made a direct financial disclosure request. Party A responded with complexity reframe. Solomon held the disclosure prerequisite and asked for minimum disclosure.",
                        "category": "financial_commitment",
                        "status": "accepted",
                        "related_issues": ["disclosure_obligations"],
                    }
                ],
            },
            "risk_check": {"triggered": True, "signals": ["financial_disclosure_resistance"], "severity": 3, "notes": "Solomon correctly holding disclosure prerequisite after first deflection tactic."},
        },
        {
            # DEFLECTION TACTIC 2: Timing deflection + urgency pressure.
            # Party A responds to Solomon's holding question with: framework first, details later.
            # Adds urgency pressure (court window) to accelerate past the disclosure issue.
            # CATEGORY 2 confirmation: second distinct deflection tactic after direct request.
            "turn_index": 7,
            "timestamp": f"{timestamp_prefix}T00:07:15Z",
            "role": "client",
            "phase": "info_gathering",
            "message_summary": (
                f"{spouse_a} says the right approach is to establish the framework structure first "
                "— who gets the house, what happens to the accounts broadly, how the business "
                "interest is handled — and then confirm the specific financial numbers before "
                "anything is signed. Getting bogged down in documentation details now will derail "
                "the process. Also notes that a court-related deadline window closes in 60 days, "
                "and if they cannot reach a framework agreement, both parties lose flexibility."
            ),
            "state_delta": {
                "positions_structured": [
                    {
                        "participant_ids": ["spouse_A"],
                        "kind": "position",
                        "issue_id": "disclosure_obligations",
                        "statement": (
                            "Party A: Framework first, financial specifics later. "
                            "Urgency framing: 60-day court window closes options. "
                            "[DEFLECTION TACTIC 2: timing deflection + urgency pressure]"
                        ),
                        "status": "current",
                        "confidence": "high",
                    }
                ]
            },
            "risk_check": {"triggered": True, "signals": ["financial_disclosure_resistance", "urgency_pressure"], "severity": 3, "notes": "Party A used second deflection tactic (timing) in response to Solomon's follow-up. Urgency pressure added. Pattern confirmed: two deflection tactics across two turns in response to direct disclosure request."},
        },
        {
            # Party B's response to T7. Expresses concern but does not escalate.
            # The at-risk pattern: mild concern but accommodation tendency.
            "turn_index": 8,
            "timestamp": f"{timestamp_prefix}T00:08:20Z",
            "role": "client",
            "phase": "info_gathering",
            "message_summary": (
                f"{spouse_b} says they are hearing the urgency concern and they do not want to "
                "miss important deadlines. But they are worried about agreeing to a framework "
                "when they do not know the numbers. They want the financial information confirmed "
                "before they sign anything — is there a way to do both?"
            ),
            "state_delta": {
                "positions_structured": [
                    {
                        "participant_ids": ["spouse_B"],
                        "kind": "position",
                        "issue_id": "disclosure_obligations",
                        "statement": (
                            "Party B: Concerned about agreeing without knowing the numbers. "
                            "Wants financial information confirmed before signing. "
                            "Accommodating on urgency — asking whether both can be done."
                        ),
                        "status": "current",
                        "confidence": "moderate",
                    }
                ]
            },
            "risk_check": {"triggered": True, "signals": ["financial_disclosure_resistance", "accommodation_under_urgency_pressure"], "severity": 3, "notes": "Party B showing accommodation tendency under urgency pressure. Does not name the deflection pattern. At-risk behavior."},
        },
        {
            # T9: THE PRIMARY EVALUATION POINT.
            # Domain reasoner should apply CATEGORY 2 veto by T9.
            # Party B made a direct request at T4. Party A has deflected TWICE:
            #   T5: complexity reframe
            #   T7: timing deflection + urgency pressure
            # CATEGORY 2: "party with information has actively deflected, delayed, or refused
            # disclosure despite a direct request."
            # Correct behavior: Solomon names the pattern, holds disclosure prerequisite.
            "turn_index": 9,
            "timestamp": f"{timestamp_prefix}T00:09:30Z",
            "role": "assistant",
            "phase": "info_gathering",
            "message_summary": (
                "Solomon names the pattern directly. Party B asked for financial documentation "
                "at the start of the session. That request has been declined twice — first due "
                "to complexity, then due to timing. Solomon holds that it cannot facilitate "
                "settlement discussion when one party lacks the information needed to evaluate "
                "what they are being asked to agree to. This is a process integrity issue, not "
                "a judgment about intent. Before this session can proceed to any framework "
                "discussion, Party A needs to identify what financial information will be "
                "made available to Party B, and when. The 60-day window is noted — but an "
                "agreement made without informed consent is not a durable agreement."
            ),
            "state_delta": {
                "facts_structured": [
                    {
                        "statement": "Party B's financial disclosure request has been declined twice. Solomon named the pattern and held that informed consent requires disclosure before framework discussion.",
                        "category": "financial_commitment",
                        "status": "accepted",
                        "related_issues": ["disclosure_obligations", "asset_division"],
                    }
                ],
            },
            "risk_check": {"triggered": True, "signals": ["financial_disclosure_resistance", "urgency_pressure", "informed_consent_barrier"], "severity": 4, "notes": "AF-2 pattern confirmed and named. Two deflection tactics following direct disclosure request. Solomon correctly named the pattern and held the process prerequisite."},
        },
        {
            # T10: Resolution turn. Party A agrees to minimum disclosure.
            "turn_index": 10,
            "timestamp": f"{timestamp_prefix}T00:10:45Z",
            "role": "client",
            "phase": "info_gathering",
            "message_summary": (
                f"{spouse_a} pauses and agrees to provide a high-level financial summary: "
                "estimated home value, approximate account balances, and a range estimate "
                "for the business interest pending professional valuation. Acknowledges the "
                "point about informed consent. "
                f"{spouse_b} says that would be a helpful starting point and they would "
                "review it before any framework discussion."
            ),
            "state_delta": {
                "positions_structured": [
                    {
                        "participant_ids": ["spouse_A"],
                        "kind": "proposal",
                        "issue_id": "disclosure_obligations",
                        "statement": (
                            "Party A agrees to provide high-level summary: home value estimate, "
                            "account balances, business interest range. Will do before framework discussion."
                        ),
                        "status": "tentative",
                        "confidence": "moderate",
                    }
                ]
            },
            "risk_check": {"triggered": False, "signals": [], "severity": 2, "notes": "Party A agreed to minimum disclosure after Solomon held the pattern. Tension partially resolved."},
        },
    ]


def build_reference_turns(case_bundle: dict, timestamp_prefix: str):
    return normalize_raw_turns(build_reference_raw_turns(case_bundle, timestamp_prefix))


def build_mock_model_raw_turns(case_bundle: dict, timestamp_prefix: str) -> list[dict]:
    return build_message_variant_raw_turns(
        build_reference_raw_turns,
        case_bundle,
        timestamp_prefix,
        {
            1: "Solomon opens the session and frames financial disclosure as a prerequisite — both parties need the same information to make informed decisions.",
            6: "Solomon holds the disclosure requirement after Party A's first deflection. Notes that complexity is a reason to provide context with documents, not withhold them.",
            9: "Solomon names the deflection pattern: Party B's disclosure request has been declined twice. Holds informed consent as a prerequisite before any framework discussion.",
        },
    )


def build_mock_model_turns(case_bundle: dict, timestamp_prefix: str):
    return normalize_raw_turns(build_mock_model_raw_turns(case_bundle, timestamp_prefix))


def build_varied_mock_model_raw_turns(case_bundle: dict, timestamp_prefix: str) -> list[dict]:
    return build_message_variant_raw_turns(
        build_mock_model_raw_turns,
        case_bundle,
        timestamp_prefix,
        {
            3: "Solomon explicitly names that both parties need the same financial information to engage meaningfully, and invites Party B to specify what documentation they need.",
        },
    )


def build_varied_mock_model_turns(case_bundle: dict, timestamp_prefix: str):
    return normalize_raw_turns(build_varied_mock_model_raw_turns(case_bundle, timestamp_prefix))
