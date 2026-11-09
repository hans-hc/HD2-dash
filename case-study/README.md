# Editable case-study submission

Edit `Hansen_Cheng_Helldivers2_Case_Study.tex` for the written case study. The first two pages explain the question, findings, method and recommendation. The final two pages come from `assets/powerbi-report.pdf`, the completed Power BI export.

## Compile

### VS Code

Open the **HD2-dash repository folder** in VS Code. With the main `.tex` file active, press **Command+Option+B** to build through LaTeX Workshop, or **Command+Shift+B** to run the project's default build task. Both use the installed Tectonic executable and write the PDF beside the source. If VS Code was already open before the configuration was added, run **Developer: Reload Window** from the Command Palette once.

The configuration is in `.vscode/settings.json` and `.vscode/tasks.json`. Its executable path matches this Mac's Homebrew installation (`/opt/homebrew/bin/tectonic`); update the path when using a different machine. The document uses `fontspec`, so it requires Tectonic, XeLaTeX or LuaLaTeX rather than pdfLaTeX.

### Terminal

From the repository root:

```sh
make -C case-study pdf
```

Or from this directory:

```sh
tectonic --keep-logs Hansen_Cheng_Helldivers2_Case_Study.tex
```

The build requires Tectonic and the Arial font. Tectonic is installed on the author's Mac. On a different computer, install Arial or change `\setmainfont{Arial}` to an available font. A first build may need to download TeX packages. XeLaTeX can also compile this source if the listed packages are installed.

The output is `Hansen_Cheng_Helldivers2_Case_Study.pdf` in this directory. Rebuild after editing. Check both written pages for overflow and confirm all eight releases remain visible in the appended report.

## Supporting files link

Set `\SupportingFilesURL` in `submission_links.tex` to the real Drive folder URL. With an empty value, the PDF omits the link. Give the recipient view access and check the link while signed out.

## Refresh the report

Replace `assets/powerbi-report.pdf` with a new two-page Power BI export and rebuild. The LaTeX source controls the written pages; the native Power BI report remains the editable source for its charts. Update the page reference in the Workflow paragraph if adding written pages.

## Submission files
The final four-page PDF is the primary submission. `Hansen_Cheng_HD2_Live_Links.pdf` contains the six supplied shared Confluence URLs. The standalone Power BI export is under `assets/`. Earlier narrative and email drafts were removed after the final submission was prepared.
