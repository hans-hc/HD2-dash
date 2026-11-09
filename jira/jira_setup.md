# Jira project record

**Project:** Helldivers 2 LiveOps Case Study · **Key:** HD2LO · Team-managed Kanban.

[Open board](https://hansencheng859.atlassian.net/jira/software/projects/HD2LO/boards/2)

The owner imported three Epics and 13 tasks, checked the hierarchy, and confirmed all 16 items Done after publishing and checking the documentation. This board records the portfolio work; it does not represent a game-team implementation or earlier project-management activity.

## Files
- `project_backlog.csv`: editable local record of purposes, acceptance criteria, evidence and completion.
- `jira_key_mapping.csv`: actual HD2LO keys observed in the owner's Jira screenshots, with direct links.
- `jira_import.csv`: initial-create import format generated from the master. **Do not reimport into HD2LO: it can create duplicates.** Its numeric IDs are import-local IDs, not existing Jira keys. Status is deliberately omitted.

The Epics are HD2LO-1 (scope; four children), HD2LO-2 (evidence; four children) and HD2LO-3 (findings/publication; five children). All items are assigned to Hansen Cheng according to the owner's completion confirmation; this repository is not a live Jira export.

For a separate fresh project only, regenerate the import with `python src/make_jira_csv.py` and map Work item ID, Work type, Parent, Summary, Description, Priority and Labels. Apply verified statuses manually. For the existing board, edit the real items using their mapped keys.

Live changes and local CSV edits do not synchronize automatically. Shared Confluence documentation is indexed in [confluence/index.md](../confluence/index.md).
