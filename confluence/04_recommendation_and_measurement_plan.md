# Investigate whether loadout variety persisted among returning players
**DRAFT — requires my review.** Reserve one analytics discovery slot to test the mechanism suggested by September. The patch notes describe broader choices against armor. Aggregate Steam activity remained above its prior baseline into days 22–35. A new Warbond and the October balance pass create plausible rival explanations. The immediate deliverable is a decision memo about whether a controlled balance test is warranted.

## Scope and requirements
Target Steam accounts with a previous completed mission, absent for a team-agreed inactivity period, who start a mission during the study entry window. Define a returning cohort using a fixed lookback and a known historical observation window. Tag new accounts, continuously active accounts, platform, patch build, DLC/Warbond exposure and difficulty separately. Predefine the inactivity period and eligibility before reading internal outcomes. The public case study supplies no player IDs.

| Requirement | Acceptance criterion |
|---|---|
| Build a reproducible returning cohort | One pseudonymous ID per eligible account. Report inclusion, exclusions, duplicate IDs and number at risk. |
| Capture mechanisms | For each mission record start/end, build, platform, squad ID, difficulty, faction, selected equipment IDs, content unlock/exposure, completion, disconnect and crash. Define joins and missingness at event level. |
| Separate exposure and repeated behavior | Report effective loadout variety across distinct missions. Distinguish new unlock availability from selection and successful mission use. Show denominators and platform strata. |
| Make a decision after complete follow-up | Freeze cohorts, wait for last entrant to mature, publish coverage, uncertainty, rival explanations and a go/revise/stop recommendation. |

## Measurements proposed for the team
**Primary.** D7 repeat mission rate among eligible returning accounts: numerator = unique cohort members completing a mission on the seventh UTC day after first return; denominator = all enrolled returning accounts with complete follow-up. Define D30 analogously as a secondary sustained check. These proposed metrics require internal data.

**Mechanism.** Measure the proportion of repeat missions using a viable alternative to the player's prior modal loadout, stratified by owned options, difficulty and armored encounters. Define viable before evaluation using mission completion and difficulty; raw weapon diversity alone can reward novelty without improved choice. Inspect whether any return improvement persists when separating Warbond users from other returning players.

**Guardrails.** Crash/disconnect sessions per eligible session, mission failure by difficulty, time to successful mission and regional/platform disparities. For a future content test also examine purchase conversion and refund/support contacts using appropriate internal denominators. Never infer sales or console activity from Steam peaks.

## Evaluation and decision
First run a retrospective cohort diagnostic across equivalent pre- and post-release entry periods, aligned by weekday. Examine existing trends, ownership, inactivity duration, returning versus continuing accounts and simultaneous patches. Results remain observational. If event coverage is too incomplete or cohort composition changes substantially, repair instrumentation or narrow the cohort before interpreting it.

If a targeted balance variation is warranted, use an opt-in test environment when feasible. Randomize eligible squads to control or one targeted balance variant, stratify by experience and difficulty, and keep content and messaging common across arms. Log exposure once per assigned squad, analyze intention to treat, limit cross-arm squad contamination, and report uncertainty accounting for squad clustering. Size the test using internal baseline rates and a pre-agreed minimum detectable effect. Enroll across at least two full weekday/weekend cycles as a design suggestion, then allow D30 maturation. If a controlled test cannot run, use a staggered rollout with comparable groups and pre-trend checks, disclosing residual selection and concurrent content effects.

**Go** only if the team approves an effect threshold, primary results meet it with adequate precision, the mechanism moves as expected, and guardrails stay within approved bounds. **Revise** for missing telemetry or imprecise estimates. **Stop** for unacceptable guardrail effects or a well-measured absence of useful benefit. Numerical thresholds, target cohort size, engineering estimates and final approval are pending. The scope excludes a promised live patch, predicted revenue and prescribing a general cadence. [Alternatives](03_options_and_prioritization.md)
