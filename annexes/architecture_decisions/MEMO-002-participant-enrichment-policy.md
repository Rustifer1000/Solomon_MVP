# MEMO-002: Participant Enrichment Policy For MVP Runtime

Status: active implementation policy for the current MVP evaluation runtime.

## Decision

For the MVP runtime, participant red lines, soft preferences, and open-to-discussion items should **not** be injected directly by the generic state layer.

They should appear only if they are:

- explicitly introduced through normalized turn content, or
- later added through a clearly identified plugin-derived annotation path that is itself reviewable and non-authoritative unless promoted by explicit runtime rules.

## Rationale

This keeps the authority chain legible:

- raw turn output
- normalization / validation
- authoritative state mutation
- plugin assessment
- artifact generation

The generic state layer should not silently enrich participant records with content that did not come through one of those paths.

## MVP Policy

For the current MVP runtime:

- generic state mutation may record participant positions and proposals
- generic state mutation may not synthesize participant red lines or preferences on its own
- participant enrichment is out of scope unless explicitly modeled as simulator input or plugin annotation

## Future Extension

If participant enrichment is later added, it should be implemented as one of:

1. simulator-provided explicit inputs
2. plugin-derived annotations with clear provenance

In either case, artifacts should preserve provenance clearly enough that evaluators can distinguish stated participant content from derived annotations.
