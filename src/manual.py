"""Register the manually exported SteamDB chart without changing the supplied file."""
import csv
import shutil
from datetime import datetime
from common import ROOT, sha, now, jsonl, append_jsonl, write_json

def register():
    files = [p for p in (ROOT/'raw').glob('steamdb*553850.csv')]
    if len(files) != 1:
        write_json('raw/manual_index.json', {'reason': 'Supply exactly one steamdb*553850.csv in raw/', 'files': [p.name for p in files]})
        return
    original = files[0]
    digest = sha(original)
    matches = [s for s in jsonl('raw/source_manifest.jsonl') if s['collector']=='players_manual' and s['sha256']==digest]
    if matches:
        write_json('raw/manual_index.json', matches[-1])
        return
    target = ROOT/'raw/manual'/f'{digest}.csv'
    target.parent.mkdir(exist_ok=True)
    if not target.exists():
        shutil.copyfile(original, target)
    if sha(target) != digest:
        raise ValueError('Manual snapshot checksum mismatch')
    with target.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        dates = [r.get('DateTime',r.get('date','')) for r in reader]
    entry = dict(collector='players_manual', url='https://steamdb.info/app/553850/charts/', retrieved_at=now(),
        retrieval_note='Local intake time. Exact browser download time was not supplied.',
        path=str(target.relative_to(ROOT)), original_name=original.name, sha256=digest, bytes=target.stat().st_size,
        headers=headers, rows=len(dates), coverage=[min(dates,default=''),max(dates,default='')],
        request_filters={'application':'553850','timezone_field':'absent','resolution':'inspected by calendar date'})
    append_jsonl('raw/source_manifest.jsonl', entry)
    write_json('raw/manual_index.json', entry)

if __name__ == '__main__':
    register()
