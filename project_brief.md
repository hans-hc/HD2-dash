# Build: Helldivers 2 LiveOps Product Management Case Study

## Context and objective

I'm a Computer Science student building my first PM-focused portfolio project for gaming or tech product management internships. My existing experience already demonstrates software development, APIs, dashboards, deployment, and real-time applications. This project should strengthen the evidence of my product judgment: framing a problem, evaluating evidence, comparing options, prioritizing, defining requirements, and proposing how to measure success.

Use real public Helldivers 2 data, Steam app ID `553850`, to answer:

> Which LiveOps events coincided with short-term spikes or sustained changes in Steam concurrency and review sentiment, and what should the team investigate or test next?

The finished work should connect evidence to one focused product recommendation. Treat the intended reader as a gaming PM or LiveOps producer evaluating a planning recommendation. This is an independent external analysis; access to Arrowhead staff, internal analytics, or actual decision-making authority is not assumed.

Core tools: Python for the data pipeline, Excel for review and prioritization, Power BI for two report pages, Jira for managing my actual project, and Confluence-ready Markdown for product documentation. Keep implementation practical and subordinate to the PM story.

Build the local code and artifacts. Document the remaining work clearly. Publishing, contacting people, creating accounts, and writing to Jira or Confluence require a separate decision.

## Scope

### Include

- A historical overview from launch, 2024-02-08, through the latest available complete UTC day.
- Three detailed event studies, subject to source verification and adequate data:
  1. The June 2024 update around 2024-06-13.
  2. The September 2024 balance overhaul around 2024-09-17.
  3. The PSN account-linking announcement and reversal around 2024-05-03 through 2024-05-06, treated as one compound policy episode.
- A comparison of short-term activity, sustained activity, sentiment, and plausible alternative explanations.
- One draft primary recommendation, compared with two alternatives.
- A proposed measurement or experiment plan for that recommendation.
- A small, honest Jira backlog and two Power BI pages.

Verify event names, versions, and dates against official announcements before using them. The dates above are research leads. Record corrections. If a candidate lacks adequate evidence, explain the gap and suggest a replacement for review; keep the total at three case studies.

### Exclude from this version

Figma, UI prototypes, SQL/database work, cloud infrastructure, Terraform, Kubernetes, Ansible, Jenkins, Puppet, Kafka, a custom web application, and a dedicated CI/CD project. Git may support normal version control. An hourly live collector, Major Orders history, four-page dashboard, and large reconstruction of historical game-development tickets are also outside the core scope.

## Ground rules

1. **Never fabricate evidence.** Every observed number must trace to a saved raw source and a documented calculation. Never invent interviews, survey responses, user counts, business impact, revenue, retention, validated development estimates, or experiment results. Qualitative effort assumptions must be labeled as assumptions.
2. **Separate evidence from judgment.** Label content as observed evidence, interpretation, assumption, or proposed action where the distinction matters. Preliminary recommendations and priorities must say `DRAFT — requires my review`.
3. **Use accurate metric names.** Steam data covers Steam users, not the entire player population. Peak concurrent players are not DAU, unique returning players, or cohort retention. Use “Steam peak concurrent players” in display labels and explicit names in data columns.
4. **Use association language.** Say “coincided with” or “was associated with.” Do not claim that a patch caused an observed change or that a public-data association proves a hypothesis.
5. **Respect source access.** Do not scrape SteamDB or bypass access restrictions. I will supply its export manually. Cache other permitted public sources, use a descriptive User-Agent, rate-limit requests to at least one second apart, and honor retry instructions. Cap retries and document persistent failures.
6. **Preserve snapshots.** Reuse cached data by default. An explicit `--refresh` may create a new timestamped snapshot without overwriting the previous raw response. Record retrieval time separately from the period the data describes.
7. **Protect human judgment.** My hypothesis wording, expected direction, decision thresholds, final priorities, and final recommendation approval remain mine. Generate templates and clearly labeled suggestions. Missing input must remain blank or pending.
8. **Keep the analysis honest about timing.** These are retrospective event studies. Hypotheses written now are retrospective, even if written before this project's charts are viewed. Do not describe them as preregistered experiments.
9. **Use Python 3.11+.** Keep dependencies small, pin working versions, and document the supported setup. Scripts must be rerunnable. Collection writes raw snapshots; curation reads raw data and explicit human inputs; analysis reads curated data and human inputs; artifact generation may write its designated output directories. Nothing should overwrite original evidence or reviewed human input.

## Repository structure

```text
README.md
SOURCES.md
data_dictionary.md
TODO_HUMAN.md
requirements.txt
.gitignore
src/
  collect.py
  curate.py
  validate.py
  analyze.py
  make_jira_csv.py
raw/
inputs/
  hypotheses.csv
  event_reviews.csv
  decision_inputs.csv
curated/
  hd2_data.xlsx
outputs/
  impact_scorecard.csv
  sensitivity_checks.csv
  validation_report.csv
  charts/
jira/
  project_backlog.csv
  jira_import.csv
  jira_setup.md
powerbi/
  queries/
  measures.dax
  model.md
  build_guide.md
  theme.json
confluence/
  index.md
  01_problem_brief.md
  02_evidence_and_event_studies.md
  03_options_and_prioritization.md
  04_recommendation_and_measurement_plan.md
  05_decision_log.md
case-study/
  case_study_draft.md
```

Add supporting files only when they serve a stated need. Keep raw SteamDB exports out of Git. Missing-data examples may demonstrate schemas, but must not contain synthetic observations that could be mistaken for real evidence.

## 1. Start with a feasibility check and problem brief

Check the available workspace, source access, and data coverage before committing to the full analysis. Record which sources are usable and which need manual help.

Create a short problem brief covering:

- The planning decision this analysis supports.
- Intended reader and their assumed information needs.
- Why this question matters for a LiveOps product.
- What public evidence can and cannot establish.
- The three candidate case studies and selection rationale.
- Deliverables, scope boundaries, assumptions, and success criteria for the project.

Project success means a reader can trace findings to evidence, understand uncertainty, compare alternatives, and assess a proposed next step. Player concurrency is an analysis metric, not a measure of whether my portfolio project succeeded.

Prepare `inputs/hypotheses.csv` with stable case IDs and blank fields for my hypothesis, expected direction, metric, threshold, and date recorded. Encourage me to complete these before viewing results. Continue independent collection and descriptive work if I have not supplied them; leave hypothesis assessments blank and add the outstanding task to `TODO_HUMAN.md`.

## 2. Collect and document public evidence

Implement `collect.py` so it accepts one or more collectors, making this command valid:

```bash
python src/collect.py reviews patches news
```

### Steam players — manual input

Look for `raw/steamdb_553850.csv`. Inspect its actual schema, resolution, date coverage, and time-zone information before parsing it.

Do not assume that an export of a zoomed chart contains complete daily history. Verify that the data supports daily peak analysis. An hourly sampled maximum must be labeled as a sampled maximum, not silently substituted for an observed daily peak. Do not expand monthly data into fabricated daily values.

If the file is missing or unsuitable, complete the independent work and document the exact input needed. Provide verified download instructions where possible; otherwise explain which step still needs checking. Leave dependent results unavailable rather than filling them in.

### Steam news and official patch notes

Use `https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/` with app ID `553850` and full content. Paginate backward using `enddate` until coverage reaches launch, or document the actual boundary. Deduplicate using stable news IDs and distinguish official announcements from third-party news feeds.

Save raw responses and a normalized table. Match the selected events to their official sources. Paraphrase key changes briefly and retain source URLs.

### Patch history

Try the Helldivers Wiki Game Version page and its MediaWiki API where accessible:

- `https://helldivers.wiki.gg/wiki/Game_Version`
- `https://helldivers.wiki.gg/api.php?action=parse&page=Game_Version&prop=text&format=json`

Use the wiki as a secondary timeline source. Cross-check selected cases against official announcements. If the wiki is inaccessible, use verified official notes for the selected cases and label the wider timeline incomplete. Do not assume an expected row count or hard-code a “latest” version.

### Steam reviews

Inspect the actual response from the public histogram endpoint, if accessible:

`https://store.steampowered.com/appreviewhistogram/553850?l=english`

Preserve raw JSON, bucket boundaries, granularity, and available filter metadata. Document the population represented, including language and off-topic filtering where known. Do not infer the review language solely from the `l` parameter.

Build a non-overlapping monthly series. Do not sum overlapping daily and monthly rollups, distribute cross-month buckets without evidence, average percentages, or treat partial months as complete months. If accurate monthly aggregation is impossible, preserve the original resolution and explain the limitation.

Daily historical sentiment for the PSN episode is optional and must actually exist in the source. If only monthly data is available, show the May context and explicitly state that it cannot distinguish the announcement from the reversal. A current review snapshot is not guaranteed to reproduce what was visible at the time of an event.

### Provenance and failures

Maintain a machine-readable source manifest and generate `SOURCES.md` from it. Include source URLs, retrieval timestamps in UTC, local paths, observed coverage, relevant filters, and checksums for saved evidence. Log unsuccessful access separately from successful retrieval.

Source failure should block only dependent work. Never silently switch to an incompatible dataset or present a source as successfully collected when it was not.

## 3. Curate tables and an Excel review workbook

Generate CSVs and named Excel Tables in `curated/hd2_data.xlsx`:

- **Players:** one row per calendar date, Steam peak concurrent players, optional average concurrent players if genuinely available, weekday, weekend flag, and a trailing seven-day mean of daily peaks. Missing observations remain blank. Require all seven observations for the rolling mean.
- **Releases:** stable release ID, version, verified date, official name, source URL, brief paraphrase, optional download size, `change_type_suggested`, `scope_suggested`, and `needs_review`.
- **Events:** stable event ID, case ID where applicable, date, event name, event type, related release ID, source URL, and verification status. Include relevant confounders when supported by sources. Link duplicate descriptions of the same event rather than counting it twice.
- **Reviews:** period start/end, positive, negative, total, percentage positive, granularity, completeness, and source/filter metadata.

Classify release scope from documented changes, with human review. Do not use download size as a rule for deciding whether an update matters. Suggested change types may include Content, Balance, Stability, Platform, Policy, or Mixed; do not force a mixed release into a misleading category.

Keep human corrections in `inputs/` with stable IDs, and apply them without overwriting the original source values. Document every table's grain, keys, types, meanings, and provenance in `data_dictionary.md`.

Include separate review sheets for event verification, hypotheses, and prioritization. Establish one authoritative editable input per judgment; document how workbook edits are saved back to `inputs/`. Rerunning the pipeline must preserve reviewed input.

## 4. Validate before interpreting

Write a pass/warn/fail report to the console and `outputs/validation_report.csv`. Check:

- Unique keys, valid dates, schema, and numeric ranges.
- Actual daily coverage, missing observations, and partial periods.
- No zero-filled gaps or duplicated review buckets.
- Selected event dates and names against official sources.
- Eligibility and observation counts for every analysis window.
- Excel and CSV consistency.

The reported Steam all-time peak of 458,709 on 2024-02-24 is a useful external spot-check if the supplied daily dataset covers it. Record the reference source and a justified tolerance. Do not change observations to match a benchmark.

Do not require a May sentiment collapse as a condition for valid data: investigate the source and filters if the expected pattern is absent. Unexpected findings are not automatically data errors.

## 5. Analyze the three event studies

For each selected anchor date, compute:

- `pre14_avg`: mean daily Steam peak concurrent players, days -14 through -1.
- `launch_window_max`: maximum daily Steam peak concurrent players, days 0 through +3.
- `day22_35_avg`: mean daily Steam peak concurrent players, days +22 through +35.
- `short_term_lift_pct = (launch_window_max - pre14_avg) / pre14_avg`.
- `sustained_lift_pct = (day22_35_avg - pre14_avg) / pre14_avg`.
- Release-month review positivity minus prior-month positivity, in percentage points, only for comparable complete months.
- Coverage counts, eligibility status, and other material events in the baseline and follow-up windows.

Require complete observations for each window: 14 baseline days, four launch-window days, and 14 later-window days. Return blank with a reason when a window crosses either data boundary or contains missing observations. Require a positive baseline for percentage lift. Treat outcomes that have not matured as pending.

Explain that short-term lift compares a maximum with an average; it is a descriptive spike measure. Do not call sustained activity “retention” or translate it into a number of individual players retained.

For the PSN episode, preserve the announcement and reversal as separate events within one case. Explain why their proximity prevents attributing a longer-window outcome to either one alone. Monthly review changes must not be presented as separate estimates of each event's sentiment effect.

Repeat baseline comparisons using seven and 28 days where complete data exists. Save these sensitivity checks and note whether the interpretation changes. Discuss existing trends, nearby releases, sales, seasonal patterns, and other evidenced alternative explanations. Do not invent statistical significance or a causal counterfactual.

These are purposefully selected examples, not a representative sample of all updates. Do not use three cases to claim an optimal release cadence or prove that one update category generally outperforms another.

Export `impact_scorecard.csv` and `sensitivity_checks.csv`. If my hypothesis and threshold are supplied, assess the descriptive result as Supported, Not supported, Inconclusive, or Confounded, with a reason. A blank hypothesis produces a blank assessment. These labels do not imply causal proof.

Create a small set of publication-ready PNGs:

1. Historical Steam daily peaks and rolling mean with selected event markers.
2. Short-term versus sustained lift scatter for eligible selected anchors, labeled as a descriptive comparison. Omit it if too few valid observations make it unhelpful.
3. Monthly positive and negative review counts with percentage positive shown appropriately.
4. A focused timeline for each case, including the baseline and follow-up periods.

Use accessible colors, accurate labels, and source footers. Titles may state a supported finding after results exist. Avoid game art and logos.

## 6. Develop a product recommendation

Create Confluence-ready Markdown pages with an index and a manual publishing guide. Include:

### Problem brief and evidence

Explain the planning question, evidence, three case studies, and uncertainty. Separate documented patch content, aggregate player activity, and review sentiment. Public reviews are self-selected feedback, not representative research on all players.

### Options and prioritization

Generate one draft primary recommendation and two meaningful alternatives based on the findings. Compare the problem addressed, intended player segment, evidence, expected benefit, risks, dependencies, and information still needed.

Use an Excel prioritization table with qualitative impact, confidence, and effort assumptions and explicit scoring definitions. Keep unknowns unknown. Numerical RICE scores are not required. Never convert Steam concurrency into estimated unique reach or present assumed effort as an engineering estimate. My final ranking remains pending until reviewed.

### Recommendation and measurement plan

For the draft primary recommendation, write a concise product proposal covering the problem, scope, non-goals, requirements, acceptance criteria, assumptions, risks, and alternatives considered. Avoid prescribing a solution the evidence does not support; further investigation may be the best recommendation.

Specify what the actual game team would need to evaluate it: proposed primary metric, guardrails, target population, instrumentation, observation period, and experimental design or alternative evaluation method. Explain internal data needed, such as D7/D30 cohort retention, returning-player behavior, console activity, or purchase conversion. Define these as proposed measurements, not data available in this project. Any target values are assumptions requiring review, not observed facts.

### Decision log and optional research

Log consequential choices, evidence, alternatives, confidence, and what would change the decision. Preliminary proposals must remain distinct from approved decisions.

Provide a short optional interview guide for relevant players and a separate guide for someone with LiveOps/analytics experience. State what each audience could help validate. Do not require interviews to finish the public-data case study, contact anyone, or fabricate findings. If no interviews occur, state that primary user research remains a limitation.

## 7. Create a small Jira backlog for my real project

Generate approximately 12-18 meaningful issues, including about three Epics, for Discovery & Scope, Evidence & Analysis, and Recommendation & Communication. Favor useful work over hitting an exact count.

Track actual portfolio work, not a fictional reconstruction of Arrowhead's internal backlog. Each issue should have a clear purpose, acceptance criteria, priority with rationale, and dependencies where real. Mark human-owned work explicitly. Use Bugs only for actual defects discovered during this project. Never claim that importing or generating an issue completes its work.

Keep a readable master backlog with stable local IDs. Generate a separate Jira Cloud import CSV, verifying the current official import documentation before selecting parent/epic fields and mappings. Local IDs are not Jira-issued keys. Document import limitations, duplicate prevention, and any required manual linking.

Provide `jira_setup.md` with project key `HD2` as a suggestion, a simple Backlog → In Progress → Review → Done workflow, and a field mapping. Prefer built-in fields. Any custom fields must have appropriate types, such as text for acceptance criteria and URLs for evidence. Explain completed versus pending work truthfully. Do not create or import anything into my Jira account automatically.

## 8. Produce Power BI build artifacts for two pages

Provide M queries with explicit types and a configurable local data-folder parameter, documented DAX measures, model instructions, a restrained dark theme with a yellow accent, and an exact build guide.

Use Python's exported impact scorecard as the authoritative event-level calculations. Power BI should display these same results rather than introduce a second set of independently defined windows. Document aggregation behavior; do not sum lift percentages or average review percentages without weighting.

Specify relationships, unique keys, table grains, and filter behavior. Use a unique daily Date key for players/events. Use a unique month dimension for monthly reviews, with deliberate month-to-date filtering where needed. A daily date table's repeating Month Start column cannot be the unique side of a relationship. Keep project-task progress distinct from game-performance evidence. Turn off auto date/time.

### Page 1 — LiveOps Overview

- Data coverage and source limitations.
- Clearly labeled Steam concurrency metrics and rolling trend.
- Verified event annotations.
- Monthly review volume and positivity.
- Date controls with documented effects on daily and monthly visuals.

### Page 2 — Event Studies & Decision Support

- Selector for the three cases.
- Scorecard with coverage and confounder indicators.
- Baseline/follow-up timeline and optional comparison scatter.
- Relevant sentiment context at its true available resolution.
- Short evidence, uncertainty, and draft recommendation summaries linked to the documentation.

Use titles supported by actual findings. Explain feasible settings and workarounds for requested visuals. Add a footer naming the actual sources, Steam-only coverage, and unofficial status.

Assume I assemble the report manually. Power BI Desktop requires a suitable Windows environment; include this prerequisite in the human checklist. Prefer saving the finished report as PBIP for version control. Generate PBIP/TMDL files only if their validity can be established; the build artifacts are sufficient otherwise.

## 9. Write the portfolio case study and handoff

### README

Include a one-line pitch, the hero chart when available, real headline findings when supported, a simple sources → analysis → evidence → recommendation diagram, reproduction instructions, source coverage, limitations, and an unofficial-project disclaimer. Never leave plausible-looking placeholder findings. Missing-data status must be clear.

### Case study

Write an approximately 1,000-1,500-word draft covering:

- The product question and why it matters.
- Scope and evidence choices.
- Three event studies with findings chosen by the data.
- Options considered and prioritization rationale.
- One draft recommendation and proposed evaluation plan.
- My pending decisions and any actual feedback received.
- Limitations and what internal data would change the analysis.

Describe completed work accurately. Hypothetical research and proposed business outcomes must remain clearly labeled. Review the wording and claims before publication.

### Human checklist

Order `TODO_HUMAN.md` by dependency: provide missing data; verify source access and event mappings; write/review retrospective hypotheses; review suggested classifications and results; make prioritization decisions; optionally conduct research; review the recommendation; set up/import Jira; assemble Power BI; publish selected documentation to Confluence; rewrite the case study; record a short walkthrough; publish the portfolio when ready.

## Definition of done and final report

Provide one documented command sequence that installs dependencies and runs collection, curation, validation, analysis, and Jira artifact generation. The command syntax must match the implemented CLI. Re-running it must preserve reviewed inputs and raw evidence.

The scope is complete when all feasible local artifacts exist, available results trace to sources, calculations and report instructions agree, and every data-dependent or human-dependent gap is explicit. Missing core data means the analysis is pending, not successfully completed. Do not inflate scope to compensate for unavailable sources.

Report back with:

1. What was delivered and what actually ran.
2. Source coverage and outstanding blockers.
3. The validation summary and event date/name corrections.
4. A comparison of the three cases, including incomplete or inconclusive results.
5. The draft recommendation, alternatives, and evidence limits.
6. Human decisions still pending and the ordered checklist.
7. Links to the local workbook, charts, Jira artifacts, Power BI guide, Confluence-ready pages, and case study.

Keep the portfolio focused on defensible product reasoning. A clearly explained inconclusive result is more useful than an unsupported recommendation.
