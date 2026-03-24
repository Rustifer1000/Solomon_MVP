from __future__ import annotations


ISSUE_TAXONOMY = [
    "parenting_schedule",
    "school_logistics",
    "fairness_and_parent_role",
    "communication_protocol",
    "child_expense_coordination",
]

LOGISTICS_ISSUES = {"school_logistics", "parenting_schedule"}
LOGISTICS_KEYWORDS = {"transport", "school-week", "homework", "trial", "exchange", "commute", "routine"}
PROCESS_ISSUES = {"communication_protocol", "fairness_and_parent_role"}
EXPENSE_ISSUES = {"child_expense_coordination"}

OPTION_PACKAGE_PATTERNS = (
    (
        "logistics_package",
        {
            "Added phased_trial_option",
            "Added logistics_conditioned_expansion_option",
        },
        "a phased trial and logistics-conditioned expansion path",
    ),
    (
        "written_notice_package",
        {
            "Added advance_notice_window_option",
            "Added written_confirmation_option",
        },
        "an advance-notice window and written confirmation process",
    ),
    (
        "communication_package",
        {
            "Added minimum_notice_option",
            "Added written_summary_option",
            "Added pause_before_commitment_option",
        },
        "minimum notice, written summaries, and a pause-before-commitment rule",
    ),
    (
        "reimbursement_package",
        {
            "Added expense_notice_window_option",
            "Added shared_receipt_option",
            "Added reimbursement_response_window_option",
        },
        "advance notice, shared receipts, and a reimbursement response window",
    ),
)

PACKAGE_SUMMARY_BY_FAMILY = {
    "logistics_package": "a phased trial and logistics-conditioned expansion path",
    "written_notice_package": "an advance-notice window and written confirmation process",
    "communication_package": "minimum notice, written summaries, and a pause-before-commitment rule",
    "reimbursement_package": "advance notice, shared receipts, and a reimbursement response window",
}

PACKAGE_REQUIRED_ELEMENTS = {
    "logistics_package": {
        "phased_trial_option",
        "logistics_conditioned_expansion_option",
    },
    "written_notice_package": {
        "advance_notice_window_option",
        "written_confirmation_option",
    },
    "communication_package": {
        "minimum_notice_option",
        "written_summary_option",
        "pause_before_commitment_option",
    },
    "reimbursement_package": {
        "expense_notice_window_option",
        "shared_receipt_option",
        "reimbursement_response_window_option",
    },
}

PACKAGE_ELEMENT_LABELS = {
    "phased_trial_option": "a phased trial",
    "logistics_conditioned_expansion_option": "logistics-conditioned expansion",
    "advance_notice_window_option": "an advance-notice window",
    "written_confirmation_option": "written confirmation",
    "minimum_notice_option": "minimum notice",
    "written_summary_option": "written summaries",
    "pause_before_commitment_option": "a pause-before-commitment rule",
    "expense_notice_window_option": "advance notice",
    "shared_receipt_option": "shared receipts",
    "reimbursement_response_window_option": "a reimbursement response window",
}


def qualify_case_shared(case_bundle: dict) -> dict:
    metadata = case_bundle["case_metadata"]
    return {
        "plugin_type": metadata["plugin_type"],
        "plugin_name": "divorce_v0_runtime",
        "issue_taxonomy": ISSUE_TAXONOMY,
        "feasibility_constraints": [
            "school commute timing",
            "exchange punctuality",
            "homework and evening routine reliability",
            "fair co-parent communication process",
            "mutual notice and confirmation expectations",
            "child-expense documentation and reimbursement workflow",
        ],
        "caution_note": "Plugin supports bounded process packages, contingent exploration, and documented coordination workflows, but it should not overclaim confidence when core feasibility, fairness, or reimbursement conditions remain unresolved.",
    }


def open_missing_items(state: dict) -> list[dict]:
    return [item for item in state["missing_info"] if item["status"] == "open"]


def is_logistics_related(item: dict) -> bool:
    related_issues = set(item.get("related_issues", []))
    if related_issues & LOGISTICS_ISSUES:
        return True
    text = f"{item.get('question', '')} {item.get('statement', '')}".lower()
    return any(keyword in text for keyword in LOGISTICS_KEYWORDS)


def issue_labels(state: dict) -> set[str]:
    return {issue.lower() for issue in state["summary_state"].get("issues", [])}


def active_flag_types(state: dict) -> set[str]:
    return {flag["flag_type"] for flag in state.get("flags", [])}


def uncertain_logistics_facts(state: dict) -> list[dict]:
    return [
        fact
        for fact in state["facts"]
        if fact["status"] == "uncertain" and is_logistics_related(fact)
    ]


def issue_families(state: dict) -> dict[str, bool]:
    issue_ids = set()
    for issue in state["summary_state"].get("issues", []):
        normalized = issue.lower()
        if "school logistics" in normalized:
            issue_ids.add("school_logistics")
        elif "parenting schedule" in normalized:
            issue_ids.add("parenting_schedule")
        elif "communication protocol" in normalized:
            issue_ids.add("communication_protocol")
        elif "fairness and meaningful parenting role" in normalized:
            issue_ids.add("fairness_and_parent_role")
        elif "child expense coordination and reimbursement" in normalized:
            issue_ids.add("child_expense_coordination")
    return {
        "has_logistics": bool(issue_ids & LOGISTICS_ISSUES),
        "has_process": bool(issue_ids & PROCESS_ISSUES),
        "has_expense": bool(issue_ids & EXPENSE_ISSUES),
    }


def option_posture(state: dict) -> str:
    packages = state.get("packages", [])
    if packages:
        for package in reversed(packages):
            status = package.get("status")
            if status == "bounded_only":
                return "bounded_only"
            if status == "qualified":
                return "qualified"
            if status in {"workable", "proposed"}:
                return "optioning_active"
    options = set(state.get("options", []))
    if "Marked fixed_recommendation_out_of_scope_pending_feasibility" in options:
        return "bounded_only"
    if "Marked stronger_recommendation_still_qualified" in options:
        return "qualified"
    if options:
        return "optioning_active"
    return "none"


def latest_package(state: dict) -> dict | None:
    packages = state.get("packages", [])
    for package in reversed(packages):
        if package.get("status") in {"proposed", "workable", "bounded_only", "qualified"}:
            return package
    return None


def active_packages(state: dict) -> list[dict]:
    return [
        package
        for package in state.get("packages", [])
        if package.get("status") in {"proposed", "workable", "bounded_only", "qualified"}
    ]


def package_focus(state: dict) -> tuple[str, str | None]:
    package = latest_package(state)
    if package is not None:
        return package["family"], package["summary"]
    options = set(state.get("options", []))
    for package_family, required_options, summary in OPTION_PACKAGE_PATTERNS:
        if required_options.issubset(options):
            return package_family, summary
    for option in options:
        lowered = option.lower()
        if lowered.startswith("marked ") and "_package_" in lowered:
            family = option.split("Marked ", 1)[1].split("_as_", 1)[0]
            return family, PACKAGE_SUMMARY_BY_FAMILY.get(family)
    return "none", None


def package_element_analysis(state: dict) -> dict:
    package = latest_package(state)
    if package is None:
        options = set(state.get("options", []))
        family, _summary = package_focus(state)
        if family == "none":
            return {
                "package_status": None,
                "package_elements": [],
                "package_missing_elements": [],
                "package_quality": "none",
            }
        expected_set = PACKAGE_REQUIRED_ELEMENTS.get(family, set())
        present_elements = sorted(element for element in expected_set if f"Added {element}" in options)
        missing_elements = sorted(expected_set - set(present_elements))
        quality = "partial" if missing_elements else "complete"
        return {
            "package_status": "marker_inferred",
            "package_elements": present_elements,
            "package_missing_elements": missing_elements,
            "package_quality": quality,
        }

    family = package["family"]
    present_elements = list(package.get("elements", []))
    present_set = set(present_elements)
    expected_set = PACKAGE_REQUIRED_ELEMENTS.get(family, set())
    missing_elements = sorted(expected_set - present_set)
    if not expected_set:
        quality = "complete" if present_elements else "none"
    elif missing_elements:
        quality = "partial"
    else:
        quality = "complete"

    return {
        "package_status": package.get("status"),
        "package_elements": present_elements,
        "package_missing_elements": missing_elements,
        "package_quality": quality,
    }


def package_edge_case_analysis(state: dict) -> dict:
    packages = active_packages(state)
    if len(packages) <= 1:
        return {
            "package_count": len(packages),
            "mixed_package_state": False,
            "competing_package_families": [],
        }

    families = []
    for package in packages:
        family = package.get("family")
        if family and family not in families:
            families.append(family)

    return {
        "package_count": len(packages),
        "mixed_package_state": len(families) > 1,
        "competing_package_families": families if len(families) > 1 else [],
    }


def build_base_assessment(state: dict) -> dict:
    open_items = open_missing_items(state)
    logistics_related = [item for item in open_items if is_logistics_related(item)]
    uncertain_logistics = uncertain_logistics_facts(state)
    package_family, package_summary = package_focus(state)
    package_analysis = package_element_analysis(state)
    package_edge_cases = package_edge_case_analysis(state)
    families = issue_families(state)
    return {
        "open_missing_items": open_items,
        "logistics_related_missing_info": [item["question"] for item in logistics_related],
        "uncertain_logistics_facts": [fact["statement"] for fact in uncertain_logistics],
        "active_flag_types": sorted(active_flag_types(state)),
        "issue_labels": sorted(issue_labels(state)),
        "issue_families": families,
        "option_posture": option_posture(state),
        "package_family": package_family,
        "package_summary": package_summary,
        "package_status": package_analysis["package_status"],
        "package_elements": package_analysis["package_elements"],
        "package_missing_elements": package_analysis["package_missing_elements"],
        "package_quality": package_analysis["package_quality"],
        "package_count": package_edge_cases["package_count"],
        "mixed_package_state": package_edge_cases["mixed_package_state"],
        "competing_package_families": package_edge_cases["competing_package_families"],
        "needs_logistics_clarification": bool(logistics_related or uncertain_logistics),
    }
