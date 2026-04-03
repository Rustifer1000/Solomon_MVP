# CLAUDE.md

## Invariants

- All API calls must go through `cached_create()` in `runtime/engine/api_utils.py`. Never call `.messages.create()` directly in any file under `runtime/engine/`. CI enforces this: `python tools/check_messages_create.py`.
- `perception_coupling_note` is a required field on every LM-generated turn — not optional.
- Escalation is a stateless priority cascade in `runtime/escalation.py`. Don't add state to it.
- Domain knowledge belongs in `runtime/plugins/`, not in the core (`runtime/orchestrator.py`, `runtime/contracts.py`, etc.).

## Tests

```bash
pytest tests/                          # must all pass
python tools/check_messages_create.py  # CI enforcement
```

## Normative authority

If docs and code conflict, `docs/01_foundations_and_architecture.md` and the files under `schema/` win. Examples in `examples/` are illustrative, not authoritative.
