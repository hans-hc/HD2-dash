# Report model
Use Import mode, one local repository root parameter, and single-direction filters. Disable automatic relationship detection on load and auto date/time in the current file. Mark Date as the date table on DateKey. Inspect Model view after refresh.

| One side | Many side | Meaning |
|---|---|---|
| Month[MonthStart] | Date[MonthStart] | A selected month constrains calendar dates. |
| Month[MonthStart] | Reviews[period_start] | Filter monthly review observations. Set one-to-many, single direction even when the current review key happens to be unique. |
| Date[DateKey] | Players[date] | One calendar row per date. Set one-to-many and single direction. |
| Date[DateKey] | Events[date] | A day can have several documented events. |
| Releases[release_id] | Events[release_id] | Release metadata filters linked events. Blank foreign keys are valid for policy and content. |
| Scorecard[case_id] | CaseTimeline[case_id] | One selected anchor per case filters 64 relative days. |

Set all relationships active. There is no relationship from Releases[date] or Date to Scorecard or CaseTimeline. Keeping page 2 independent ensures a page 1 date slicer cannot truncate the windows. Date[MonthStart] repeats and belongs on the many side. Reviews has one row per month. The separate raw review bucket table is excluded. A day slicer affects Players and Events only. Month affects both daily and monthly facts. Never relate monthly counts to every day of the month.

Scorecard contains the exported 14-day calculations, without duplicated reversal rows. Set numeric columns to Don't summarize wherever the model permits. Measures explicitly choose MAX for an observed peak, SELECTEDVALUE for one case, and a ratio of summed counts for positivity. Missing values stay blank. Disable totals on comparisons of lifts, percentages, or event-only attributes. No project-management data participates in this model.
