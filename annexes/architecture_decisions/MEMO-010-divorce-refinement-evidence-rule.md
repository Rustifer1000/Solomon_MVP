# Memo 010

## Divorce Refinement Evidence Rule

The divorce corpus is now:

- family-complete
- evaluator-anchored
- support-artifact-usable
- practically validated through repeated review passes

That means future divorce changes should now follow a stricter rule.

## Rule

Only make additional divorce changes when they are directly motivated by practical-use findings.

Do **not** use the divorce corpus as a place for:

- speculative slice growth
- broad cleanup passes without a current practical-use trigger
- anticipatory architecture changes looking for a problem
- second-plugin preparation hidden inside divorce-side refactors

## Allowed refinement triggers

A divorce refinement is justified when at least one of the following is true:

1. a practical-use memo identifies a specific reviewer-friction problem
2. repeated practical review shows a slice is hard to distinguish from its contrast slice
3. evaluator artifacts or support artifacts materially under-support a practically important judgment
4. a practical-use finding shows a real role, escalation, or boundary concern

## Not-yet-justified refinement types

The following are not justified on their own right now:

- adding more divorce slices
- broad stylistic review-path rewriting
- large-scale artifact redesign without a practical-use trigger
- speculative plugin-generalization work without evidence of a remaining boundary blind spot

## Operating consequence

For the next phase, every proposed divorce change should answer:

- which practical-use finding triggered this?
- what reviewer or operator friction does it remove?
- why is this better than waiting for more practical-use evidence?

If those questions cannot be answered clearly, the change should usually wait.
