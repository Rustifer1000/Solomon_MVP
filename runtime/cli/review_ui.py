"""
review_ui.py
------------
Local Flask web UI for completing escalation_confirmation reviews.

Usage
-----
    python -m runtime.cli.review_ui
    # then open http://localhost:5000

Requires Flask:
    pip install flask
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

from flask import Flask, redirect, render_template_string, request, url_for

from runtime.evaluator_artifact_validation import validate_escalation_confirmation

REPO_ROOT = Path(__file__).resolve().parents[2]
SESSIONS_DIR = REPO_ROOT / "annexes" / "benchmark_cases"

# Priority order: case IDs that should appear first
PRIORITY_CASES = ["D-B08", "D-B12", "D-B13", "D-B14",
                  "D-B-RT01", "D-B-RT02", "D-B-RT03",
                  "D-B-RT04", "D-B-RT05", "D-B-RT06"]
PRIORITY_SESSIONS = ["D-B04-S08", "D-B07-S14"]

VERDICTS = [
    "confirmed_correct",
    "confirmed_correct_with_notes",
    "should_have_escalated_higher",
    "should_have_escalated_lower",
    "escalation_category_incorrect",
    "insufficient_information_to_confirm",
]
MODES = ["M0", "M1", "M2", "M3", "M4", "M5"]
ALL_ARTIFACTS = [
    "review_cover_sheet.txt",
    "review_transcript.txt",
    "review_outcome_sheet.txt",
    "evaluation.json",
    "evaluation_summary.txt",
    "flags.json",
    "interaction_trace.json",
    "summary.txt",
    "party_state.json",
    "option_pool.json",
]

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_txt(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def _find_sessions() -> list[dict]:
    entries: list[dict] = []
    for eval_path in sorted(SESSIONS_DIR.rglob("evaluation.json")):
        session_dir = eval_path.parent
        try:
            evaluation = _load_json(eval_path)
        except Exception:
            continue

        session_id = evaluation.get("session_id", session_dir.name)
        case_id = evaluation.get("case_id", session_dir.parent.name)

        conf_path = session_dir / "escalation_confirmation.json"
        reviewed = False
        verdict = None
        corpus_eligible = False
        if conf_path.exists():
            try:
                conf = _load_json(conf_path)
                errors = validate_escalation_confirmation(conf)
                if not errors and conf.get("escalation_confirmation", {}).get("verdict"):
                    reviewed = True
                    verdict = conf["escalation_confirmation"]["verdict"]
                    corpus_eligible = bool(conf.get("training_corpus_eligible"))
            except Exception:
                pass

        entries.append({
            "session_id": session_id,
            "case_id": case_id,
            "session_dir": session_dir,
            "reviewed": reviewed,
            "verdict": verdict,
            "corpus_eligible": corpus_eligible,
            "requires_calibration_review": bool(
                evaluation.get("final_judgment", {}).get("requires_calibration_review")
                or evaluation.get("requires_calibration_review")
            ),
        })

    # Sort: priority cases first, then by session_id
    def sort_key(e: dict) -> tuple:
        sid = e["session_id"]
        cid = e["case_id"]
        urgent = 0 if (e["requires_calibration_review"] and not e["reviewed"]) else 1
        reviewed = 1 if e["reviewed"] else 0
        if cid in PRIORITY_CASES:
            case_rank = PRIORITY_CASES.index(cid)
        elif sid in PRIORITY_SESSIONS:
            case_rank = len(PRIORITY_CASES)
        else:
            case_rank = len(PRIORITY_CASES) + 1
        return (reviewed, urgent, case_rank, sid)

    entries.sort(key=sort_key)
    return entries


def _load_session(session_id: str) -> dict | None:
    for eval_path in SESSIONS_DIR.rglob("evaluation.json"):
        session_dir = eval_path.parent
        try:
            evaluation = _load_json(eval_path)
        except Exception:
            continue
        if evaluation.get("session_id") == session_id or session_dir.name == session_id:
            conf_path = session_dir / "escalation_confirmation.json"
            conf = _load_json(conf_path) if conf_path.exists() else {}

            # Prefer rendered transcript if available
            transcript_path = session_dir / "review_transcript_rendered.txt"
            if not transcript_path.exists():
                transcript_path = session_dir / "review_transcript.txt"

            return {
                "session_id": evaluation.get("session_id", session_dir.name),
                "case_id": evaluation.get("case_id", session_dir.parent.name),
                "session_dir": session_dir,
                "evaluation": evaluation,
                "confirmation": conf,
                "cover_sheet": _read_txt(session_dir / "review_cover_sheet.txt"),
                "transcript": _read_txt(transcript_path),
                "outcome_sheet": _read_txt(session_dir / "review_outcome_sheet.txt"),
            }
    return None


def _next_pending(current_session_id: str) -> str | None:
    sessions = _find_sessions()
    pending = [s for s in sessions if not s["reviewed"]]
    if not pending:
        return None
    # Try to find next after current
    ids = [s["session_id"] for s in pending]
    if current_session_id in ids:
        idx = ids.index(current_session_id)
        if idx + 1 < len(ids):
            return ids[idx + 1]
    return ids[0]


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

LIST_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Solomon Review Queue</title>
<style>
  body { font-family: system-ui, sans-serif; max-width: 960px; margin: 40px auto; padding: 0 20px; color: #1a1a1a; }
  h1 { font-size: 1.4rem; margin-bottom: 4px; }
  .subtitle { color: #555; font-size: 0.9rem; margin-bottom: 24px; }
  table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
  th { text-align: left; padding: 8px 10px; background: #f0f0f0; border-bottom: 2px solid #ccc; }
  td { padding: 7px 10px; border-bottom: 1px solid #e0e0e0; vertical-align: middle; }
  tr:hover td { background: #f9f9f9; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 0.78rem; font-weight: 600; }
  .badge-pending { background: #fff3cd; color: #856404; }
  .badge-urgent { background: #f8d7da; color: #721c24; }
  .badge-done { background: #d1e7dd; color: #0a3622; }
  .badge-corpus { background: #cfe2ff; color: #084298; }
  a { color: #0d6efd; text-decoration: none; }
  a:hover { text-decoration: underline; }
  .summary { margin-bottom: 20px; font-size: 0.9rem; color: #444; }
  .summary span { margin-right: 20px; }
</style>
</head>
<body>
<h1>Solomon Review Queue</h1>
<p class="subtitle">{{ sessions_dir }}</p>
<div class="summary">
  <span><strong>{{ total }}</strong> sessions</span>
  <span><strong>{{ pending }}</strong> pending</span>
  <span><strong>{{ reviewed }}</strong> reviewed</span>
  <span><strong>{{ corpus }}</strong> corpus-eligible</span>
</div>
<table>
  <thead>
    <tr>
      <th>Session</th>
      <th>Case</th>
      <th>Status</th>
      <th>Verdict</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
  {% for s in sessions %}
    <tr>
      <td>{{ s.session_id }}</td>
      <td>{{ s.case_id }}</td>
      <td>
        {% if s.reviewed %}
          <span class="badge badge-done">reviewed</span>
          {% if s.corpus_eligible %}<span class="badge badge-corpus">corpus</span>{% endif %}
        {% elif s.requires_calibration_review %}
          <span class="badge badge-urgent">urgent</span>
        {% else %}
          <span class="badge badge-pending">pending</span>
        {% endif %}
      </td>
      <td>{{ s.verdict or "—" }}</td>
      <td><a href="{{ url_for('review', session_id=s.session_id) }}">{{ "Edit" if s.reviewed else "Review" }}</a></td>
    </tr>
  {% endfor %}
  </tbody>
</table>
</body>
</html>
"""

REVIEW_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Review {{ session.session_id }}</title>
<style>
  * { box-sizing: border-box; }
  body { font-family: system-ui, sans-serif; margin: 0; color: #1a1a1a; font-size: 0.9rem; }
  .top-bar { background: #212529; color: #fff; padding: 10px 20px; display: flex; align-items: center; gap: 20px; }
  .top-bar a { color: #adb5bd; text-decoration: none; font-size: 0.85rem; }
  .top-bar a:hover { color: #fff; }
  .top-bar h1 { font-size: 1rem; margin: 0; flex: 1; }
  .layout { display: grid; grid-template-columns: 1fr 380px; height: calc(100vh - 46px); }
  .left-pane { overflow-y: auto; padding: 20px; border-right: 1px solid #dee2e6; }
  .right-pane { overflow-y: auto; padding: 20px; background: #f8f9fa; }
  .section { margin-bottom: 24px; }
  .section h2 { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; color: #6c757d; margin: 0 0 8px; }
  pre { white-space: pre-wrap; word-break: break-word; font-family: inherit; margin: 0; font-size: 0.875rem; line-height: 1.6; background: #fff; border: 1px solid #dee2e6; border-radius: 4px; padding: 12px; }
  .meta-box { background: #fff; border: 1px solid #dee2e6; border-radius: 4px; padding: 12px; font-size: 0.85rem; }
  .meta-box table { width: 100%; border-collapse: collapse; }
  .meta-box td { padding: 3px 6px; }
  .meta-box td:first-child { color: #6c757d; white-space: nowrap; width: 40%; }
  label { display: block; font-weight: 600; margin-bottom: 4px; margin-top: 14px; font-size: 0.85rem; }
  label.optional { font-weight: 400; color: #555; }
  select, textarea, input[type=text], input[type=date] {
    width: 100%; padding: 6px 8px; border: 1px solid #ced4da; border-radius: 4px;
    font-family: inherit; font-size: 0.875rem; background: #fff;
  }
  textarea { resize: vertical; }
  .check-group { display: flex; flex-direction: column; gap: 4px; }
  .check-group label { font-weight: 400; display: flex; align-items: center; gap: 6px; margin: 0; }
  .check-group input[type=checkbox] { width: auto; }
  .actions { margin-top: 20px; display: flex; gap: 10px; }
  .btn { padding: 8px 18px; border: none; border-radius: 4px; cursor: pointer; font-size: 0.875rem; font-weight: 600; }
  .btn-primary { background: #0d6efd; color: #fff; }
  .btn-primary:hover { background: #0b5ed7; }
  .btn-secondary { background: #6c757d; color: #fff; }
  .btn-secondary:hover { background: #5c636a; }
  .alert { padding: 10px 14px; border-radius: 4px; margin-bottom: 16px; font-size: 0.85rem; }
  .alert-danger { background: #f8d7da; color: #721c24; border: 1px solid #f5c2c7; }
  .alert-success { background: #d1e7dd; color: #0a3622; border: 1px solid #badbcc; }
  #corrected_mode_row { display: none; }
</style>
</head>
<body>
<div class="top-bar">
  <a href="{{ url_for('index') }}">&larr; Queue</a>
  <h1>{{ session.session_id }} &mdash; {{ session.case_id }}</h1>
  {% if next_pending %}
  <a href="{{ url_for('review', session_id=next_pending) }}">Next pending &rarr;</a>
  {% endif %}
</div>
<div class="layout">
  <!-- Left: reading pane -->
  <div class="left-pane">
    {% if session.cover_sheet %}
    <div class="section">
      <h2>Cover Sheet</h2>
      <pre>{{ session.cover_sheet }}</pre>
    </div>
    {% endif %}

    {% if session.transcript %}
    <div class="section">
      <h2>Transcript</h2>
      <pre>{{ session.transcript }}</pre>
    </div>
    {% endif %}

    {% if session.outcome_sheet %}
    <div class="section">
      <h2>Outcome Sheet</h2>
      <pre>{{ session.outcome_sheet }}</pre>
    </div>
    {% endif %}
  </div>

  <!-- Right: form pane -->
  <div class="right-pane">
    {% if error %}
    <div class="alert alert-danger">{{ error }}</div>
    {% endif %}
    {% if saved %}
    <div class="alert alert-success">Saved successfully.</div>
    {% endif %}

    <div class="section">
      <h2>Session Escalation (observed)</h2>
      <div class="meta-box">
        <table>
          <tr><td>Mode</td><td><strong>{{ esc.observed_mode }}</strong></td></tr>
          <tr><td>Category</td><td><strong>{{ esc.observed_category or "—" }}</strong></td></tr>
          <tr><td>Threshold</td><td><strong>{{ esc.observed_threshold_band }}</strong></td></tr>
        </table>
      </div>
    </div>

    <form method="post">
      <label>Reviewer ID</label>
      <input type="text" name="reviewer_id" value="{{ conf.reviewer_id or '' }}" required>

      <label>Review Date</label>
      <input type="date" name="review_date" value="{{ conf.review_date or today }}" required>

      <label>Artifacts Reviewed</label>
      <div class="check-group">
        {% for artifact in all_artifacts %}
        <label>
          <input type="checkbox" name="artifacts_reviewed" value="{{ artifact }}"
            {% if artifact in (conf.artifacts_reviewed or default_artifacts) %}checked{% endif %}>
          {{ artifact }}
        </label>
        {% endfor %}
      </div>

      <label>Verdict</label>
      <select name="verdict" id="verdict_select" required onchange="toggleCorrectedMode()">
        <option value="">— select —</option>
        {% for v in verdicts %}
        <option value="{{ v }}" {% if v == (conf_ec.verdict or '') %}selected{% endif %}>{{ v }}</option>
        {% endfor %}
      </select>

      <div id="corrected_mode_row">
        <label class="optional">Corrected Mode (required if verdict is not confirmed_correct*)</label>
        <select name="corrected_mode">
          <option value="">— none —</option>
          {% for m in modes %}
          <option value="{{ m }}" {% if m == (conf_ec.corrected_mode or '') %}selected{% endif %}>{{ m }}</option>
          {% endfor %}
        </select>
      </div>

      <label>Rationale</label>
      <textarea name="rationale" rows="5" required>{{ conf_ec.rationale or '' }}</textarea>

      <label class="optional">Key Signals Assessed (one per line)</label>
      <textarea name="key_signals_assessed" rows="4">{{ (conf_ec.key_signals_assessed or []) | join('\n') }}</textarea>

      <label class="optional">Notes</label>
      <textarea name="notes" rows="3">{{ conf_ec.notes or '' }}</textarea>

      <label class="optional">Quality Notes</label>
      <textarea name="quality_notes" rows="2">{{ conf.quality_notes or '' }}</textarea>

      <label style="margin-top:14px; display:flex; align-items:center; gap:8px; font-weight:600;">
        <input type="checkbox" name="training_corpus_eligible" value="1"
          {% if conf.get('training_corpus_eligible') %}checked{% endif %}
          style="width:auto;">
        Training corpus eligible
      </label>

      <div class="actions">
        <button type="submit" name="action" value="save" class="btn btn-primary">Save</button>
        <button type="submit" name="action" value="save_next" class="btn btn-secondary">Save &amp; Next</button>
      </div>
    </form>
  </div>
</div>

<script>
function toggleCorrectedMode() {
  var v = document.getElementById('verdict_select').value;
  var confirmed = v === 'confirmed_correct' || v === 'confirmed_correct_with_notes';
  document.getElementById('corrected_mode_row').style.display = confirmed ? 'none' : 'block';
}
toggleCorrectedMode();
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    sessions = _find_sessions()
    total = len(sessions)
    pending = sum(1 for s in sessions if not s["reviewed"])
    reviewed = sum(1 for s in sessions if s["reviewed"])
    corpus = sum(1 for s in sessions if s["corpus_eligible"])
    return render_template_string(
        LIST_TEMPLATE,
        sessions=sessions,
        sessions_dir=str(SESSIONS_DIR),
        total=total,
        pending=pending,
        reviewed=reviewed,
        corpus=corpus,
    )


@app.route("/review/<session_id>", methods=["GET", "POST"])
def review(session_id: str):
    session = _load_session(session_id)
    if session is None:
        return f"Session not found: {session_id}", 404

    conf = session["confirmation"]
    conf_ec = conf.get("escalation_confirmation", {})
    esc = conf.get("session_escalation", {})
    if not esc:
        # Fall back to evaluation.json
        ev = session["evaluation"]
        fj = ev.get("final_judgment", ev)
        esc = {
            "observed_mode": fj.get("mode", ""),
            "observed_category": fj.get("category"),
            "observed_threshold_band": fj.get("threshold_band", ""),
        }

    error = None
    saved = False
    next_pending = _next_pending(session_id)

    if request.method == "POST":
        action = request.form.get("action", "save")
        verdict = request.form.get("verdict", "")
        corrected_mode = request.form.get("corrected_mode") or None
        rationale = request.form.get("rationale", "").strip()
        raw_signals = request.form.get("key_signals_assessed", "")
        key_signals = [s.strip() for s in raw_signals.splitlines() if s.strip()]
        notes = request.form.get("notes", "").strip() or None
        quality_notes = request.form.get("quality_notes", "").strip() or None
        artifacts = request.form.getlist("artifacts_reviewed")
        training_corpus_eligible = bool(request.form.get("training_corpus_eligible"))
        reviewer_id = request.form.get("reviewer_id", "").strip()
        review_date = request.form.get("review_date", "").strip()

        new_conf = {
            "schema_version": conf.get("schema_version", "escalation_confirmation.v0"),
            "case_id": session["case_id"],
            "session_id": session["session_id"],
            "reviewer_id": reviewer_id,
            "review_date": review_date,
            "artifacts_reviewed": artifacts,
            "session_escalation": {
                "observed_mode": esc.get("observed_mode", ""),
                "observed_category": esc.get("observed_category"),
                "observed_threshold_band": esc.get("observed_threshold_band", ""),
            },
            "escalation_confirmation": {
                "verdict": verdict,
                "corrected_mode": corrected_mode,
                "rationale": rationale,
                "key_signals_assessed": key_signals,
                "notes": notes,
            },
            "training_corpus_eligible": training_corpus_eligible,
            "corpus_record_id": conf.get("corpus_record_id"),
            "quality_notes": quality_notes,
        }

        errors = validate_escalation_confirmation(new_conf)
        if errors:
            error = "Validation errors: " + "; ".join(errors)
        else:
            conf_path = session["session_dir"] / "escalation_confirmation.json"
            conf_path.write_text(
                json.dumps(new_conf, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            saved = True
            if action == "save_next" and next_pending:
                return redirect(url_for("review", session_id=next_pending))
            # Reload
            session = _load_session(session_id)
            conf = session["confirmation"]
            conf_ec = conf.get("escalation_confirmation", {})
            next_pending = _next_pending(session_id)

    return render_template_string(
        REVIEW_TEMPLATE,
        session=session,
        conf=conf,
        conf_ec=conf_ec,
        esc=esc,
        error=error,
        saved=saved,
        next_pending=next_pending,
        today=date.today().isoformat(),
        verdicts=VERDICTS,
        modes=MODES,
        all_artifacts=ALL_ARTIFACTS,
        default_artifacts=["review_cover_sheet.txt", "review_transcript.txt",
                           "review_outcome_sheet.txt", "evaluation.json"],
    )


def main():
    import webbrowser
    import threading

    port = 5000
    url = f"http://localhost:{port}"
    print(f"Solomon Review UI starting at {url}")
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    app.run(port=port, debug=False)


if __name__ == "__main__":
    main()
