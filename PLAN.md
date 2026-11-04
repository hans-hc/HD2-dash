# Implementation plan

The brief is implemented as a local, reproducible portfolio project. No accounts,
remote publication, Jira import, or Confluence write is part of this implementation.

1. **Feasibility:** inspect the empty repository, preserve the brief, verify public
   endpoints and official event mappings, identify manual evidence requirements.
2. **Pipeline:** immutable cached snapshots → typed CSV curation → window eligibility
   and analysis → validation. Preserve all human inputs on repeated runs.
3. **Review artifacts:** named Excel Tables, explicit input handoff, honest coverage
   status, accessible charts, source manifest and data dictionary.
4. **Product reasoning:** three retrospective cases, three options, a draft proposal,
   measurement design, decisions and research guides, portfolio narrative.
5. **Handoff and verification:** small actual-work Jira backlog, two-page Power BI
   build kit, boundary tests, full rerun and evidence/input preservation checks.

Completion means feasible local artifacts and explicit gaps. Concurrency analysis
remains pending until an eligible manually supplied daily-peak dataset exists.
Final priorities, hypotheses, thresholds and approval belong to the project owner.

## Delivery record
All five local stages ran. The supplied SteamDB export made all main and sensitivity
windows eligible. Validation finished with 70 passes and four disclosed warnings.
Four boundary tests passed. A separate checkout verified a real workbook edit
round-trip, protected stale copies, the portable writer and missing-export behavior.
The cached rerun preserved 25 original-source and input hashes.

The owner checklist contains the remaining review, Desktop assembly and publication
steps. See README.md for the evidence comparison and the exact reproduction command sequence.
