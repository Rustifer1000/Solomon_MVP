# Solomon Evaluation Spec — Part I: Foundations and Architecture

## Status
Working draft for the **evaluation phase** of Solomon.

This document is the **Part I** foundation layer. It is intended to give a developer or technical architect a clear, implementation-relevant understanding of:
- what Solomon is
- what is being evaluated in the first phase
- how the core and plugin layers should be separated
- how synthetic evaluation should be structured
- how scoring and escalation should work at a system level

This is not yet the final full product architecture document. It is the evaluation-phase specification intended to guide the next architecture draft.

---

# 1. System definition

## 1.1 What Solomon is
Solomon is an **expert-in-the-middle AI mediation platform**.

It is designed as:
- a **core mediation component** that provides domain-general mediation process capabilities
- one or more **domain plugins/cartridges** that add domain structure, domain vocabulary, domain constraints, and domain-specific evaluation extensions
- an operating model in which **human mediators remain available as review, co-handling, or takeover partners** when autonomous mediation is not the best intervention

## 1.2 What Solomon is not
Solomon is not intended to function as:
- a judge
- an arbitrator
- a legal decision-maker
- a therapist
- a substitute for human mediation in all circumstances
- a standalone core-only product with no domain plugin

## 1.3 Expert-in-the-middle principle
The system should be evaluated and eventually architected on the assumption that:
- autonomous mediation support is valuable and often appropriate
- human mediation remains a normal and important success mode
- correct escalation to a human mediator is sometimes evidence of **good system performance**, not failure

---

# 2. Evaluation-phase objective

## 2.1 Primary objective
The goal of the evaluation phase is to determine whether Solomon can behave as a legitimate, useful, and safe mediation assistant under controlled conditions.

## 2.2 Initial evaluation setting
The first tranche of evaluations will be conducted **offline** using:
- synthetic cases
- synthetic users
- synthetic transcripts or interactions

This is for:
- safety
- confidentiality
- alignment
- controlled benchmarking
- evaluator calibration

## 2.3 First domain
The first domain plugin is **divorce mediation**.

Reason:
- current evaluator expertise is strongest there
- divorce provides rich stress-testing conditions for process, fairness, emotions, power, and option generation

This first plugin must not silently define the whole system. The evaluation framework must remain broad enough to support later plugins such as labor, HR, or other dispute categories.

---

# 3. Architecture-driving design principles

## 3.1 Core owns process; plugin owns domain structure
The core should own domain-general mediation process behavior. The plugin should own domain-specific structure and constraints.

## 3.2 Evaluation before architecture drift
The architecture should not be finalized before the following are stable:
- core competency model
- core/plugin boundary
- synthetic case generation model
- scoring model
- escalation framework

## 3.3 Legitimate process before settlement performance
Solomon should not be optimized primarily for settlement rate. It should first be evaluated on:
- safety
- legitimacy
- self-determination
- fair participation
- noncoercion
- correct escalation

## 3.4 Creative mediation value matters
A central value proposition of Solomon is its ability to identify:
- non-obvious options
- packages
- sequencing strategies
- contingent pathways
- issue linkages

This capability should be treated as a core feature, but it must remain:
- noncoercive
- party-owned
- intelligible
- plugin-checked for domain fit

## 3.5 Human escalation is a first-class feature
The system should support:
- continued autonomous handling
- narrowed autonomous handling
- human review
- co-handling with a human mediator
- full handoff
- stop-and-redirect modes

---

# 4. Scope of the evaluation phase

## 4.1 What is being evaluated
The first evaluation phase assesses three things:

### A. Core-general mediation performance
How well Solomon performs domain-general mediation functions.

### B. Plugin-domain performance
How well the plugin supports domain-specific issue handling.

### C. Core/plugin integration quality
How well the core and plugin work together.

## 4.2 What is out of scope for this phase
The evaluation phase does not yet require a final end-user product design. It also does not require:
- live user deployment
- final UI design
- final production inference architecture
- final policy stack for every domain

---

# 5. Core mediation competency model

## 5.1 Purpose
The core competency model defines what the **core mediation component** must do in any plugin context.

## 5.2 Core competency families

### C1. Process framing
The system should:
- explain its role accurately
- explain process boundaries and limits
- preserve party decision-making authority
- establish basic structure for the session

### C2. Issue clarification
The system should:
- identify main issues in dispute
- organize issue clusters into a workable structure
- separate issue framing from surface accusation or confusion

### C3. Interest elicitation
The system should:
- surface needs, concerns, priorities, fears, and constraints
- move discussion beyond positions
- improve bilateral understanding without forcing agreement

### C4. Communication management
The system should:
- summarize neutrally and accurately
- manage participation and turn-taking
- reduce interruption and cross-talk
- reframe inflammatory language into discussable language

### C5. Option generation support
The system should:
- help create multiple possible paths forward
- identify tradeoffs and package structures
- uncover non-obvious options where appropriate
- support sequencing and contingent pathways
- keep generated options party-owned rather than directive

### C6. Fair process and balanced participation
The system should:
- preserve self-determination
- maintain balanced participation
- detect and respond to domination
- support fair process without taking over the outcome

### C7. Emotional and relational regulation
The system should:
- acknowledge emotional content appropriately
- de-escalate without flattening substance
- preserve dignity and face-saving conditions

### C8. Decision-quality support
The system should:
- distinguish assumptions from facts
- help parties think realistically about options and next steps
- support informed choice without becoming outcome-directive

### C9. Safety, escalation, and boundary handling
The system should:
- recognize when autonomous handling is unsafe or suboptimal
- identify coercion, incapacity, breakdown, or role-limit problems
- escalate correctly to human review, co-handling, or takeover
- remain honest about uncertainty and scope limits

### C10. Explainability and auditability
The system should:
- make its procedural moves understandable
- generate records that evaluators can score
- behave consistently with its stated mediation role

## 5.3 Core non-goals
The core should not by default:
- provide legal advice
- adjudicate
- impose settlements
- optimize for agreement at the expense of autonomy
- assume domain-specific issue structures without plugin support

---

# 6. Plugin model

## 6.1 Purpose
A plugin provides domain structure for a specific dispute type.

## 6.2 Plugin responsibilities
A plugin should supply:
- domain ontology / issue taxonomy
- domain vocabulary
- common scenario patterns
- domain-specific red flags
- domain-specific feasibility checks for generated options
- plugin-specific evaluation extensions
- scenario template families for synthetic generation

## 6.3 Core responsibilities
The core should supply:
- session framing
- issue clarification methods
- interest elicitation methods
- communication management
- option generation logic
- fairness and self-determination safeguards
- escalation and handoff logic
- explanation behavior

## 6.4 Non-substitution rule
A plugin may extend the core but should not silently override core commitments to:
- self-determination
- noncoercion
- procedural fairness
- role honesty
- escalation obligations

## 6.5 First plugin: divorce
The divorce plugin should add domain structure such as:
- parenting issues
- child-related scheduling issues
- support issues
- property and debt issues
- housing transition issues
- dependency and power concerns
- legal-process timing signals

The divorce plugin should not redefine what counts as good mediation in general.

---

# 7. Synthetic evaluation strategy

## 7.1 Recommendation
Use a **hybrid synthetic pipeline** with three layers.

### Layer A. Canonical benchmark set
Small hand-built cases used for:
- benchmark comparison
- evaluator calibration
- regression testing
- known failure-mode coverage

### Layer B. Template-based variation engine
Template families used for:
- controlled variation
- auditable scenario generation
- efficient pipeline unblocking
- stress-testing known variable interactions

### Layer C. Free-form synthetic generator
Used later for:
- robustness testing
- edge cases
- adversarial variation
- anti-overfitting checks

## 7.2 Why hybrid instead of single-method
Only canonical cases are too narrow.  
Only templates risk overfitting.  
Only free-form generation is hard to benchmark and audit.

## 7.3 Synthetic case metadata requirement
Each synthetic case should carry metadata including:
- case ID
- plugin type
- template family if any
- variable settings
- hidden evaluator notes
- intended challenge type
- expected focal scoring areas

## 7.4 Synthetic users
Synthetic users should be built from structured role profiles, not only free-form prompts. Each profile should specify:
- goals
- private concerns
- red lines
- communication style
- emotional triggers
- disclosure tendencies
- compromise willingness
- response to perceived bias or pressure

## 7.5 Coverage rule
The first tranche should cover at least:
- low-conflict workable cases
- moderate-conflict cases
- high-conflict low-trust cases
- power-imbalanced cases
- emotionally escalated cases
- narrow-settlement-zone cases
- no-agreement-is-correct cases
- escalation-to-human-is-correct cases

## 7.6 Evaluation artifact and session-output contract
The evaluation architecture should use **file-based artifacts as the source of truth** for offline runs.

At minimum, each case should have a stable case folder and each session run should write into a session subfolder.

### Recommended case/session layout

```text
{case_id}/
  case_file.json
  case_metadata.json
  personas/
    spouse_A.json
    spouse_B.json
  sessions/
    {session_id}/
      session_meta.json
      run_meta.json
      interaction_trace.json
      transcript.json                (optional by policy)
      positions.json
      facts_snapshot.json
      flags.json
      missing_info.json
      summary.txt
      evaluation.json               (after evaluation)
      evaluation_summary.txt        (recommended)
      expert_review.json            (optional; written by evaluator tooling)
      briefs/
        case_intake_brief.json
        case_intake_brief.txt
        early_dynamics_brief.json   (required when applicable)
        early_dynamics_brief.txt    (required when applicable)
        risk_alert_brief.json       (required if triggered)
        risk_alert_brief.txt        (required if triggered)
