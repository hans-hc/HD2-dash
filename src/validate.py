"""Check data integrity and window eligibility; FAIL exits nonzero, WARN is disclosed."""
import argparse
from collections import Counter
from datetime import date,datetime,timedelta
from math import isclose
from statistics import mean
from common import *
from curate import SCHEMAS,ANCHOR_GIDS,PSN,month_end
from studies import ANCHORS,study_outputs
from workbook import packets,OUT

def validate(stage):
    report=[]
    def record(name,status,detail):report.append(dict(check=name,status=status,detail=detail))
    def check(name,test,detail):record(name,'PASS' if test else 'FAIL',detail)
    def coverage(name,test,detail):record(name,'PASS' if test else 'WARN',detail)
    manifests=jsonl('raw/source_manifest.jsonl')
    for m in manifests:
        p=ROOT/m['path']
        if not p.exists() and m['collector']=='players_manual':
            record('Raw snapshot '+m['path'],'WARN','Private manual snapshot absent from this checkout')
        else:check('Raw checksum '+m['path'],p.exists() and sha(p)==m['sha256'],'SHA-256 compared with saved manifest')
    keys={'players':['date'],'releases':['release_id'],'events':['event_id'],'reviews':['period_start'],'review_buckets':['series','bucket_start'],'news':['news_id']}
    for name,cols in keys.items():
        path='curated/'+name+'.csv';rows=read_csv(path)
        with (ROOT/path).open() as f: schema=next(csv.reader(f))
        check(name+' schema',schema==SCHEMAS[name].split(),', '.join(cols)+' form the key')
        ids=[tuple(r[c] for c in cols) for r in rows]
        check(name+' unique keys',len(ids)==len(set(ids)) and all(all(k) for k in ids),f'{len(ids)} rows')
    p=read_csv('curated/players.csv');cov=read_json('curated/coverage.json')
    start,end=date.fromisoformat(cov['calendar_start']),date.fromisoformat(cov['calendar_end'])
    check('Complete calendar',[r['date'] for r in p]==[str(d) for d in days(start,end)],f'{start} through {end}')
    peaks=[number(r['steam_peak_concurrent_players']) for r in p]
    n=sum(v is not None for v in peaks)
    manual=read_json('raw/manual_index.json',{})
    if n and manual.get('path'):
        original={r['DateTime']:r for r in read_csv(manual['path'])}
        reconciled=all(original.get(r['date']+' 00:00:00',{}).get('Players')==r['steam_peak_concurrent_players'] for r in p if r['steam_peak_concurrent_players']!='')
        check('Daily peaks / original CSV',reconciled,f'{n} exact integer comparisons; no imputation')
    coverage('Daily peak coverage',n==len(p),f'{n}/{len(p)} days have daily peaks. See observation_method for excluded days.')
    check('Player numeric range',all(v is None or v>=0 and v.is_integer() for v in peaks),'Nonnegative integral counts')
    check('No filled gaps',all((r['observation_method']=='daily chart rollup' or v is None) for r,v in zip(p,peaks)),'Missing/sampled rows have blank peak values')
    rolling=True
    for i,r in enumerate(p):
        seq=peaks[max(0,i-6):i+1];actual=number(r['steam_peak_7d_mean'])
        if len(seq)==7 and None not in seq:rolling &= actual is not None and isclose(actual,mean(seq))
        else:rolling &= actual is None
    check('Rolling seven observations',rolling,'Every daily value independently checked')
    bench=next((r['steam_peak_concurrent_players'] for r in p if r['date']=='2024-02-24'),'')
    coverage('Peak spot-check',bench=='458709',f'2024-02-24 export = {bench or "missing"} vs 458,709. Tolerance 0: integral same-source published record. No adjustment.')
    coverage('Timestamp basis',False,cov['players'].get('timezone','Source timezone unavailable'))
    reviews=read_csv('curated/reviews.csv')
    check('Monthly count and percentage identity',all(int(r['positive'])>=0 and int(r['negative'])>=0 and int(r['total'])==int(r['positive'])+int(r['negative']) and
        (isclose(float(r['pct_positive']),int(r['positive'])/int(r['total'])) if int(r['total']) else r['pct_positive']=='') for r in reviews),'Weighted positivity = positive / total')
    bounds=[(date.fromisoformat(r['period_start']),date.fromisoformat(r['period_end'])) for r in reviews]
    check('Non-overlapping calendar months',all(s.day==1 and e==month_end(s) for s,e in bounds) and all(a[1]<b[0] for a,b in zip(bounds,bounds[1:])),'Monthly table uses one series at a time')
    partial=[r['period_start'] for r in reviews if r['completeness']!='complete']
    coverage('Partial review months',not partial,'Excluded from month comparisons: '+', '.join(partial))
    news={r['news_id']:r for r in read_csv('curated/news.csv')}
    ix=read_json('raw/news_index.json',{})
    if ix.get('pages'):
        expected=read_json(ix['pages'][0])['appnews'].get('count')
        coverage('News history',len(news)==expected or ix['stop_reason']=='reached_launch',
            f'{len(news)} unique IDs; first response reports {expected}; boundary {ix["oldest_date"]}, {ix["stop_reason"]}')
    coverage('Historical review series',bool(reviews),f'{len(reviews)} calendar month buckets')
    for name,key,allowed in [('hypotheses','case_id',{c['case_id'] for c in CASES}),('decision_inputs','option_id',{'investigate_balance','content_cadence','policy_comms'})]:
        ids=[r[key] for r in read_csv('inputs/'+name+'.csv')]
        check(name+' input IDs',len(ids)==len(set(ids)) and set(ids)==allowed,'Expected stable IDs appear once each')
    events={r['event_id']:r for r in read_csv('curated/events.csv')}
    for gid,case in ANCHOR_GIDS.items():
        e=events.get(ANCHORS[case]);s=news.get(gid)
        if not s or not e:
            record('Official mapping '+case,'WARN','Missing official record');continue
        check('Official mapping '+case,s['official']=='True' and s['title']==e['source_name'] and s['date']==e['source_date'] and gid in e['related_news_ids'].split('|'),s['date']+' '+s['title'])
    reversal=events.get('psn-reversal')
    if PSN in news:
        content=next(x['contents'] for x in read_json(news[PSN]['source_path'])['appnews']['newsitems'] if x['gid']==PSN)
        check('PSN amendment',reversal and reversal['source_date']=='2024-05-06' and 'UPDATE 5/6/2024' in content and 'will not be moving forward' in content,'One source, two events, one case')
    releases=read_csv('curated/releases.csv')
    check('Release links',all(not e['release_id'] or e['release_id'] in {r['release_id'] for r in releases} for e in events.values()),'Every linked release resolves')
    differences=[r['release_id'] for r in releases if r['wiki_date'] and r['wiki_date']!=r['source_date']]
    coverage('Secondary date discrepancies',not differences,'Inspect in Releases: '+', '.join(differences))
    for r in releases+list(events.values()):date.fromisoformat(r['date'])
    check('Timeline date range',all(start<=date.fromisoformat(e['date'])<=end for e in events.values()),'Dates parsed and checked against analysis horizon')
    main,sens,_=study_outputs()
    for r in main+sens:
        coverage(f"{r['case_id']} {r['baseline_days']}d baseline",r['activity_status']=='eligible',
            f"{r['baseline_n']}/{r['baseline_days']}, {r['launch_n']}/4, {r['later_n']}/14. {r['activity_status']}")
    if stage=='all':
        from openpyxl import load_workbook
        from openpyxl.utils.cell import range_boundaries
        w=load_workbook(OUT,data_only=True)
        for tab in packets():
            sh=w[tab['name']];t=sh.tables[tab['name'].replace(' ','')+'Table'];left,top,right,bottom=range_boundaries(t.ref)
            headers=[sh.cell(top,j).value for j in range(left,right+1)]
            ok=headers==tab['columns'] and bottom-top==max(1,len(tab['rows']))
            for i,row in enumerate(tab['rows'],top+1):
                for j,expected in enumerate(row,left):
                    val=sh.cell(i,j).value
                    if isinstance(val,(date,datetime)):val=((val.date() if isinstance(val,datetime) else val)-date(1899,12,30)).days
                    if isinstance(expected,(int,float)) and isinstance(val,(int,float)):ok &= isclose(expected,val,rel_tol=1e-12,abs_tol=1e-12)
                    else:ok &= val==expected
            check('Excel / CSV '+tab['name'],ok,f"{len(tab['rows'])} rows and all columns reconciled")
        for filename,expected in [('impact_scorecard',main),('sensitivity_checks',sens)]:
            exported=read_csv('outputs/'+filename+'.csv')
            check('Export '+filename,len(exported)==len(expected) and all(all(r[k]==('' if v is None else str(v)) for k,v in e.items()) for r,e in zip(exported,expected)),'Recomputed from curated tables and human inputs')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--stage',choices=['data','all'],default='all')
    try: rows=validate(parser.parse_args().stage)
    except Exception as err:rows=[dict(check='Validation execution',status='FAIL',detail=f'{type(err).__name__}: {err}')]
    write_csv('outputs/validation_report.csv',rows,['check','status','detail'])
    for r in rows:print(r['status'],r['check'],r['detail'])
    totals=Counter(r['status'] for r in rows);print('Totals',dict(totals))
    raise SystemExit(bool(totals['FAIL']))
