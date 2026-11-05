"""Build the Excel review copy or explicitly import edits to the authoritative CSVs."""
import argparse
import csv
from datetime import date,datetime
import json
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from common import ROOT, read_csv, read_json, write_csv, write_json, sha

OUT=ROOT/'curated/hd2_data.xlsx'
STATE='curated/workbook_state.json'
INPUTS={'Hypotheses':'hypotheses','Event review':'event_reviews','Prioritization':'decision_inputs'}
OPTIONS={
    'investigate_balance':('Investigate returning players and loadout variety','High','Medium','Unknown','September remained above baseline. Verify cohort behavior and competing content exposure.'),
    'content_cadence':('Evaluate patch and Warbond timing','Unknown','Low','Unknown','Selected Nov 5: eight releases show mixed outcomes for similar gaps. No optimal gap established.'),
    'policy_comms':('Test clearer account-policy communication','Medium','Low','Unknown','May reviews identify risk. Communication effectiveness and affected audiences remain unknown.')}
NUMBERS=set('positive negative total pct_positive steam_peak_concurrent_players average_concurrent_players sampled_max_concurrent_players sample_count steam_peak_7d_mean final_rank threshold baseline_n launch_n later_n short_term_lift_pct sustained_lift_pct review_change_pp pre14_avg launch_window_max day22_35_avg'.split())
NUMBERS.update('baseline_avg baseline_days cluster_to_content_days cluster_baseline_avg week1_avg week2_avg week3_avg week1_n week2_n week3_n cluster_sustained_lift_pct cluster_short_term_lift_pct week1_lift_pct week2_lift_pct week3_lift_pct'.split())
DATES={'date','source_date','period_start','period_end','wiki_date','date_override','date_recorded','anchor_date','release_date','announcement_date','cluster_anchor'}
BOOL={'is_weekend','needs_review'}
def revision():
    hashes=[sha(ROOT/'inputs'/(name+'.csv')) for name in INPUTS.values()]
    return hashlib.sha256('|'.join(hashes).encode()).hexdigest()
def fields(path):
    with (ROOT/path).open(encoding='utf-8-sig',newline='') as f:return next(csv.reader(f))

def packet(name,title,note,cols,rows,editable=()):
    def value(k,v):
        if v in ('',None):return None
        if k in NUMBERS: return float(v)
        if k in DATES: return (date.fromisoformat(str(v))-date(1899,12,30)).days
        if k in BOOL: return v is True or str(v).lower()=='true'
        return v
    return dict(name=name,title=title,note=note,columns=cols,rows=[[value(k,r.get(k)) for k in cols] for r in rows],editable=list(editable),
        dates=[c for c in cols if c in DATES],percent=[c for c in cols if c=='pct_positive' or c.endswith('_lift_pct')])

def packets():
    scores=read_csv('outputs/impact_scorecard.csv')
    cards='event_name anchor_date short_term_lift_pct sustained_lift_pct review_change_pp baseline_n launch_n later_n activity_status'.split()
    sheets=[packet('Decision brief','The launch spike and the later window','Steam daily peaks • short and sustained lift vs. prior 14 days • review change in percentage points',cards,scores)]
    sheets[0]['review_revision']=revision()
    dcols=fields('inputs/decision_inputs.csv')
    ds=[]
    for r in read_csv('inputs/decision_inputs.csv'):
        name,impact,conf,effort,basis=OPTIONS[r['option_id']]
        ds.append(dict(r,option=name,impact_suggested=impact,confidence_suggested=conf,effort_assumption=effort,evidence_and_risk=basis))
    sheets.append(packet('Prioritization','Options for the next discovery slot','Content timing selected November 5. Amber fields retain unanswered ratings and approvals.',
        ['option_id','option','impact_suggested','confidence_suggested','effort_assumption','evidence_and_risk']+dcols[1:],ds,dcols[1:]))
    path='inputs/hypotheses.csv';cols=fields(path)
    sheets.append(packet('Hypotheses','Retrospective hypotheses','Enter your own wording, direction, metric, threshold and actual date. Record whether results were already seen.',cols,read_csv(path),cols[1:]))
    path='inputs/event_reviews.csv';cols=fields(path); submitted={r['event_id']:r for r in read_csv(path)}
    releases={r['release_id']:r for r in read_csv('curated/releases.csv')}
    rows=[]
    for e in read_csv('curated/events.csv'):
        rel=releases.get(e['release_id'],{})
        rows.append(dict(source_date=e['source_date'],source_name=e['source_name'],change_type_suggested=rel.get('change_type_suggested'),scope_suggested=rel.get('scope_suggested'),source_url=e['source_url'],**submitted.get(e['event_id'],{'event_id':e['event_id']})))
    sheets.append(packet('Event review','Verify dates, names and classifications','Filter by event ID. Amber fields are optional corrections. Give the evidence URL and reviewer for a correction.',
        ['event_id','source_date','source_name','change_type_suggested','scope_suggested','source_url']+cols[1:],rows,cols[1:]))
    for name,note in [('Players','Manual SteamDB chart • daily peaks and subdaily sampled maxima are separate series.'),('Releases','Official Steam news and secondary wiki timeline • classifications require review.'),
        ('Events','Official posts, scheduled content and secondary timeline entries • see verification and linked news IDs.'),('Reviews','Steam histogram • positive / total by calendar month • partial periods are labeled.')]:
        path='curated/'+name.lower()+'.csv'
        sheets.append(packet(name,name,note,fields(path),read_csv(path)))
    path='outputs/content_timing_scorecard.csv'
    timing=read_csv(path)
    if not timing:
        raise SystemExit('Missing content-timing scorecard. Run src/content_timing.py before workbook.py.')
    cols='name release_date cluster_to_content_days short_term_lift_pct week1_lift_pct week2_lift_pct week3_lift_pct sustained_lift_pct'.split()
    sheets.append(packet('Content timing','Patch and Warbond release timing',
        'Python snapshot. All activity changes use the prior 14-day average daily Steam peak as baseline.',cols,timing))
    labels=['Warbond','Release date','Patch gap (days)','Launch max vs baseline','Week 1 mean vs baseline','Week 2 mean vs baseline','Week 3 mean vs baseline','Later mean vs baseline']
    sheets[-1]['columns']=labels
    sheets[-1]['dates']=['Release date']
    sheets[-1]['percent']=labels[3:]
    sheets[-1]['annotations']=[
        [16,'Finding: Similar release gaps produced mixed later activity. This sample establishes no preferred gap.'],
        [18,'Recommendation: Compare similar content scopes before changing cadence. Review launch, weekly and later activity.'],
        [20,'Launch = days 0–3 maximum. Weeks = days 0–6, 7–13, 14–20 means. Later = days 22–35 mean.'],
        [22,'Gap = days from earliest official patch within the preceding seven days, including release day. Hotfixes count.'],
        [24,'Steam concurrency describes aggregate activity. It does not identify retained players or isolate a release effect.']]
    cols='content_id name release_date announcement_date date_basis date_evidence source_url source_path news_id baseline_avg baseline_n launch_window_max launch_n day22_35_avg later_n preceding_patch_ids preceding_patch_dates cluster_anchor cluster_baseline_avg cluster_sustained_lift_pct activity_status cluster_activity_status'.split()
    sheets.append(packet('Timing evidence','Release dates and calculation evidence',
        'Official announcement bodies supply release dates. Scheduled dates are distinguished from same-day availability.',cols,timing))
    return sheets

def fallback(sheets,target):
    """Portable writer using the project's pinned Python dependencies."""
    from openpyxl import Workbook
    from openpyxl.styles import Font,PatternFill
    from openpyxl.worksheet.table import Table,TableStyleInfo
    from openpyxl.utils import get_column_letter as letter
    w=Workbook();w.remove(w.active)
    for s in sheets:
        sh=w.create_sheet(s['name']);sh.sheet_view.showGridLines=False
        sh['A2']=s['title'];sh['A2'].font=Font(name='Arial',size=16,bold=True,color='173443');sh['A3']=s['note']
        for j,k in enumerate(s['columns'],1):
            sh.cell(5,j,k);sh.column_dimensions[letter(j)].width=max(16,min(60,len(k)+5))
        for row in s['rows']:sh.append(row)
        for j,k in enumerate(s['columns'],1):
            for i in range(6,6+len(s['rows'])):
                cell=sh.cell(i,j)
                if k in s['dates']:cell.number_format='yyyy-mm-dd'
                if k in s['percent']:cell.number_format='0.0%'
                if k in s['editable']:cell.fill=PatternFill('solid',fgColor='FFF1C5')
        last=max(6,5+len(s['rows']));t=Table(displayName=s['name'].replace(' ','')+'Table',ref=f'A5:{letter(len(s["columns"]))}{last}')
        t.tableStyleInfo=TableStyleInfo(name='TableStyleMedium2',showRowStripes=True,showColumnStripes=False);sh.add_table(t);sh.freeze_panes='B6'
        if 'review_revision' in s:
            sh['A12']='Input revision';sh['B12']=s['review_revision']
        for row,text in s.get('annotations',[]):sh.cell(row,1,text)
    w.save(target)

def build(preview=False):
    state=read_json(STATE,{})
    if OUT.exists() and (not state or sha(OUT)!=state.get('workbook_sha256')):
        raise SystemExit('Workbook has unsaved-to-CSV edits. Save a copy, then run workbook.py --import-edits PATH before regenerating.')
    sheets=packets()
    runtime_path=os.environ.get('HD2_RUNTIME')
    runtime=Path(runtime_path) if runtime_path else None
    with tempfile.TemporaryDirectory() as tmp:
        tmp=Path(tmp);target=tmp/'hd2_data.xlsx'
        if runtime and (runtime/'node/bin/node').exists() and (runtime/'node/node_modules/@oai/artifact-tool').exists():
            node=runtime/'node/bin/node';mods=runtime/'node/node_modules'
            (tmp/'node_modules').symlink_to(mods,target_is_directory=True)
            shutil.copy(ROOT/'src/workbook.mjs',tmp/'build.mjs')
            if OUT.exists():shutil.copyfile(OUT,tmp/'existing.xlsx')
            (tmp/'data.json').write_text(json.dumps(sheets))
            subprocess.run([str(node),'build.mjs',str(ROOT/'outputs/workbook_previews') if preview else ''],cwd=tmp,check=True)
        else: fallback(sheets,target)
        OUT.parent.mkdir(exist_ok=True)
        shutil.copyfile(target,OUT.with_suffix('.tmp'));OUT.with_suffix('.tmp').replace(OUT)
    write_json(STATE,dict(workbook_sha256=sha(OUT),inputs={v:sha(ROOT/'inputs'/(v+'.csv')) for v in INPUTS.values()}))
    print('Saved',OUT)

def import_edits(file):
    from openpyxl import load_workbook
    from openpyxl.utils.cell import range_boundaries
    state=read_json(STATE)
    if not state:raise SystemExit('Missing generation state. Use a workbook from this checkout.')
    w=load_workbook(file,data_only=False)
    if w['Decision brief']['B12'].value!=revision():
        raise SystemExit('This workbook copy predates the current inputs. Reconcile its edits against current stable IDs.')
    changes={}
    for tab,name in INPUTS.items():
        p=ROOT/'inputs'/(name+'.csv')
        if sha(p)!=state['inputs'][name]:raise SystemExit('Inputs changed since export: '+name+'. Reconcile edits in a copy first.')
        columns=fields(p);sh=w[tab];table=sh.tables[tab.replace(' ','')+'Table']
        _,start,_,end=range_boundaries(table.ref)
        headers={c.value:c.column for c in sh[start]}
        rows=[];seen=set()
        allowed={r[columns[0]] for r in read_csv(p)} if name!='event_reviews' else {r['event_id'] for r in read_csv('curated/events.csv')}
        for i in range(start+1,end+1):
            row={}
            for k in columns:
                c=sh.cell(i,headers[k]);v=c.value
                if c.data_type=='f':raise ValueError('Input must be a literal value: '+c.coordinate)
                if isinstance(v,(date,datetime)):v=v.strftime('%Y-%m-%d')
                row[k]='' if v is None else str(v)
            key=row[columns[0]]
            if not key and not any(row.values()):continue
            if key not in allowed or key in seen:raise ValueError('Unknown or duplicate input key: '+key)
            seen.add(key)
            if name!='event_reviews' or any(row[k] for k in columns[1:]):rows.append(row)
        if seen!=allowed:raise ValueError('Stable input IDs were removed from '+tab)
        if rows!=read_csv(p):changes[p]=(rows,columns)
    archive=ROOT/'inputs/archive'/datetime.now().strftime('%Y%m%dT%H%M%S%f')
    for p,(rows,columns) in changes.items():
        archive.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,archive/p.name)
        tmp=p.with_suffix('.tmp');write_csv(tmp,rows,columns);tmp.replace(p)
    # Once the explicit import has succeeded, allow the edited canonical workbook to rebuild.
    if Path(file).resolve()==OUT.resolve():
        state['workbook_sha256']=sha(OUT);write_json(STATE,state)
    print('Imported changes to',len(changes),'input tables; rerun curation through validation.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--preview',action='store_true');p.add_argument('--import-edits',type=Path)
    a=p.parse_args()
    if a.import_edits:import_edits(a.import_edits)
    else:build(a.preview)
