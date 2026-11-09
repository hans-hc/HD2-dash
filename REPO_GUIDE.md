# Quick repository guide

## Read the project in ten minutes
1. Open [the final PDF](case-study/Hansen_Cheng_Helldivers2_Case_Study.pdf) for the story and Power BI visuals.
2. Read [content timing](case-study/content_timing.md) for the measurement choices and caveats.
3. Open [Excel](curated/hd2_data.xlsx), starting with **Content timing** and **Timing evidence**. Other sheets support the original three-event research and input review.
4. Read the [recommendation](confluence/04_recommendation_and_measurement_plan.md) and [decision log](confluence/05_decision_log.md).

## Trace a number back to evidence
For a Warbond, start at `outputs/content_timing_scorecard.csv`:
- Match `content_id` to `inputs/content_releases_2024.csv`. Its source path, news ID and date cue identify the saved official announcement.
- Daily observations come from `curated/players.csv`.
- `src/content_timing.py` selects the patch sequence and calculates weekly comparisons. `src/studies.py` calculates baseline, launch and later windows.
- `outputs/content_timing_sensitivity.csv` repeats the comparison with 7-day and 28-day baselines. Alternative patch-sequence results are in the main timing scorecard.
- `outputs/content_timing_timeline.csv` contains the relative-day observations.
- [SOURCES.md](SOURCES.md), `curated/source_register.csv` and the raw manifest record provenance. The original SteamDB export is private and excluded from Git.

## Edit the right file
| Change | File or location |
|---|---|
| Final written PDF | `case-study/Hansen_Cheng_Helldivers2_Case_Study.tex`; rebuild with `make -C case-study pdf` |
| Drive URL in PDF | `case-study/submission_links.tex`; rebuild |
| Power BI charts | Edit the live Power BI report, export both pages, replace `case-study/assets/powerbi-report.pdf`, rebuild |
| Written project documentation | `confluence/*.md`; update the published pages separately |
| Verified Warbond dates | `inputs/content_releases_2024.csv`; retain the official evidence |
| Workbook review inputs | Follow `inputs/README.md`; import a reviewed copy before regenerating |
| Jira completion record | `jira/project_backlog.csv` and `jira/jira_key_mapping.csv`; update the live board separately |

## Supporting research versus final analysis
`impact_scorecard.csv`, `sensitivity_checks.csv`, `case_timeline.csv` and the June/September/PSN figures cover the original three events. The files prefixed `content_timing_` cover the final eight-Warbond study. Keep both: the workbook and validation still use the earlier research.

`raw/` holds evidence, `curated/` holds cleaned data, and `outputs/` holds calculated results. The `.venv/` folder is a local Python environment, not a submission artifact.

## Checks
Run `.venv/bin/python -m unittest discover -s tests` for the six automated checks. Run `.venv/bin/python src/validate.py` for dataset and workbook consistency checks; this rewrites the saved validation report. Read warnings rather than treating a passing exit code as proof that all source limitations are resolved.
