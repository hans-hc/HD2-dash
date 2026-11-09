# Power BI report

The completed report was built in **Power BI web on a Mac**. Its editable version lives in the Power BI account; the repository contains the [two-page PDF export](../case-study/assets/powerbi-report.pdf). No Desktop report, PBIX file or authored Desktop model is included.

## Data
Import the named **ContenttimingTable** from [curated/hd2_data.xlsx](../curated/hd2_data.xlsx). Use one row per Warbond. Patch gap is a whole number; launch, weekly and later changes are fractions displayed as percentages with one decimal place. Release date is a date.

## Pages
1. **Activity Comparison:** clustered horizontal bars by Warbond comparing launch maximum (days 0–3) with later average (days 22–35), relative to the preceding 14-day baseline.
2. **Release Timing:** an eight-row table and eight-point scatter plot. X is patch gap in days; Y is later activity change; Warbond identifies each point. Include the finding, recommendation, method and source footer.

Before exporting, clear selections and filters, confirm all eight releases are visible, and check that charts display as charts rather than the viewing-mode table preview. Export both pages. Replace `case-study/assets/powerbi-report.pdf`, then rebuild the final case study.

The unused Desktop query/model/DAX build kit was removed during cleanup because it does not describe the report actually built.
