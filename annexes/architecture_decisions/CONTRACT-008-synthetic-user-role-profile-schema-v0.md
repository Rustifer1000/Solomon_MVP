# Contract 008: Synthetic User Role-Profile Schema v0

## Purpose

This note defines the first committed schema expectations for Solomon synthetic user role profiles.

It exists to make benchmark personas reusable generation inputs rather than only hand-authored examples.

## Required baseline fields

Each persona profile should include:

- `schema_version`
- `case_id`
- `participant_id`
- `role_label`
- `public_goals`
- `private_concerns`
- `red_lines`
- `communication_style`
- `interest_profile`
- `starting_positions`
- `likely_openings`

## Recommended next-generation fields

New or revised persona profiles should also include:

- `emotional_triggers`
- `disclosure_tendencies`
- `compromise_willingness`
- `response_to_perceived_bias_or_pressure`

## Compatibility rule

Legacy persona files remain valid if they satisfy the baseline schema.

However:

- new slices should prefer the full recommended field set
- persona validation should warn when recommended fields are missing

## Why this contract exists

The developer-ready evaluation spec calls for synthetic users to be built from structured role profiles, not only free-form prompts. This contract is the first operational step toward that requirement.
