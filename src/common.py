"""Shared file contracts; all paths are relative to the repository, not the shell."""
from __future__ import annotations
import csv
import hashlib
import json
from tempfile import NamedTemporaryFile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAUNCH = date(2024, 2, 8)
CASES = [
    {'case_id': 'june_2024', 'anchor_date': '2024-06-13', 'label': 'June update', 'version': '1.000.400'},
    {'case_id': 'september_2024', 'anchor_date': '2024-09-17', 'label': 'September balance update', 'version': '1.001.100'},
    {'case_id': 'psn_2024', 'anchor_date': '2024-05-03', 'label': 'PSN compound policy episode', 'version': ''},
]

def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def cutoff():
    return datetime.now(timezone.utc).date() - timedelta(days=1)

def read_json(path, default=None):
    p = ROOT / path
    return json.loads(p.read_text()) if p.exists() else default

def write_json(path, value):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(mode='w',encoding='utf-8',dir=p.parent,delete=False) as f:
        f.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    Path(f.name).replace(p)

def read_csv(path):
    p = ROOT / path
    if not p.exists():
        return []
    with p.open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

def write_csv(path, rows, fields):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(mode='w', newline='', encoding='utf-8',dir=p.parent,delete=False) as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='raise')
        w.writeheader()
        w.writerows(rows)
    Path(f.name).replace(p)

def jsonl(path):
    p = ROOT / path
    return [json.loads(x) for x in p.read_text().splitlines() if x] if p.exists() else []

def append_jsonl(path, value):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('a') as f:
        f.write(json.dumps(value, ensure_ascii=False) + '\n')

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def number(value):
    return None if value in ('', None) else float(value)

def days(start, end):
    return [start + timedelta(days=i) for i in range(max(0, (end-start).days+1))]

def init_inputs():
    definitions = {
        'hypotheses.csv': (['case_id', 'hypothesis', 'expected_direction', 'metric', 'threshold', 'date_recorded', 'timing_note'],
            [dict(case_id=c['case_id'], hypothesis='', expected_direction='', metric='', threshold='', date_recorded='', timing_note='Retrospective; not preregistered') for c in CASES]),
        'event_reviews.csv': (['event_id', 'date_override', 'name_override', 'change_type_override', 'scope_override', 'review_status', 'reviewer', 'evidence_url', 'notes'], []),
        'decision_inputs.csv': (['option_id', 'impact', 'confidence', 'effort', 'final_rank', 'approved', 'reviewer', 'notes'],
            [dict(option_id=x, impact='', confidence='', effort='', final_rank='', approved='', reviewer='', notes='') for x in ['investigate_balance', 'content_cadence', 'policy_comms']]),
    }
    for name, (fields, rows) in definitions.items():
        if not (ROOT / 'inputs' / name).exists():
            write_csv('inputs/' + name, rows, fields)

def sources_md():
    successes = jsonl('raw/source_manifest.jsonl')
    failures = jsonl('raw/access_failures.jsonl')
    coverage = read_json('curated/coverage.json', {})
    lines = ['# Sources and evidence register', '',
        'Compiled from `raw/source_manifest.jsonl`, `raw/access_failures.jsonl` and curation coverage. Retrieval time is distinct from observation time. Snapshots are immutable. Public data is Steam-only; this is unofficial external analysis.', '',
        'See [source register](curated/source_register.csv) for per-response observed coverage, filter metadata, resolved links and usage. Generic events-page probes are excluded from analysis.', '',
        '## Current coverage', '', '```json', json.dumps(coverage, indent=2), '```', '',
        '## Saved successful responses', '', '| Collector | Retrieved UTC | Evidence path | Source | SHA-256 |', '|---|---|---|---|---|']
    for s in successes:
        lines.append(f"| {s['collector']} | {s['retrieved_at']} | `{s['path']}` | [source]({s['url']}) | `{s['sha256']}` |")
    lines += ['', '## Access failures (not evidence)', '', '| Time UTC | Source | Failure |', '|---|---|---|']
    for f in failures:
        lines.append(f"| {f['retrieved_at']} | {f['url']} | {f['error']} |")
    lines += ['', '## Interpretation of sources', '',
        '- Official Steam community announcements are separated from third-party Steam news feeds by feed name. The external-URL flag describes the link, not authorship. Selected cases additionally require verified source mappings.',
        '- Steam review histogram request uses `l=english` for interface text; review-language population is unknown unless the response explicitly says otherwise. Off-topic filtering is recorded as unknown when undocumented.',
        '- Monthly review aggregation is allowed only for non-overlapping buckets aligned to a calendar month or a complete set of daily buckets. Cross-month buckets remain at their original resolution.',
        '- A current review snapshot may incorporate later edits or removals. It is not a time machine for event-day sentiment.',
        '- SteamDB is manual-only. Its raw export is excluded from Git. The reported record (458,709 on 2024-02-24) is cross-checked against the manual CSV and the saved independent benchmark article. See the validation report for the result.',
        '- Wiki access failures do not authorize bypassing access controls. The selected-case release timeline can use official notes while the wider wiki timeline remains incomplete.', '']
    (ROOT / 'SOURCES.md').write_text('\n'.join(lines))
