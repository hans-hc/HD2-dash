"""Summarize observed content per saved response separately from retrieval time."""
from datetime import datetime,timezone
from common import ROOT,jsonl,read_json,write_csv
def entries():
    results=[]
    for m in jsonl('raw/source_manifest.jsonl'):
        kind=m['collector']; path=m['path'];period=''; filters='';use=''
        if kind=='news':
            items=read_json(path)['appnews']['newsitems']
            dates=[datetime.fromtimestamp(x['date'],timezone.utc).date().isoformat() for x in items]
            period=(min(dates)+' to '+max(dates)) if dates else 'empty page'
            filters='appid=553850; all feeds; maxlength=0';use='News ID and source feed'
        elif kind=='reviews':
            d=read_json(path);r=d['results']
            period=' to '.join(datetime.fromtimestamp(r[k],timezone.utc).date().isoformat() for k in ('start_date','end_date'))
            filters=f"l=english; count_all_reviews={d.get('count_all_reviews')}; language and off-topic policy unknown"
            use='rollup_type='+str(r.get('rollup_type'))+'; overlapping recent array retained separately'
        elif kind=='players_manual':
            period=' to '.join(m['coverage']);filters='manual chart export; timezone not declared';use='Original file and hash-addressed private snapshot'
        elif kind=='patches':
            import re
            dates=re.findall(r'\b20\d\d-\d\d-\d\d\b',str(read_json(path)['parse']['text']['*']) if path.endswith('.json') else (ROOT/path).read_text())
            period=(min(dates)+' to '+max(dates)) if dates else 'not determined';use='Secondary version table'
        elif kind=='official_pages':
            use='Diagnostic only: generic events listing; excluded from case verification'
        elif kind=='patch_crosscheck':period='2024-09-18';use='Wiki version alias; compared with Steam hotfix contents'
        elif kind=='benchmark':period='2024-02-24';use='Independent report of SteamDB peak for exact-count spot-check'
        elif kind=='anchor_pages':
            period={'6890025005348276470':'2024-06-13','6250522009530732352':'2024-09-17','5766372999945329774':'2024-05-03 and dated 2024-05-06 amendment'}.get(m['url'].split('/')[-1],'')
            use='Official selected-case page at resolved URL'
        results.append(dict(collector=kind,source_url=m.get('final_url',m['url']),retrieved_at=m['retrieved_at'],path=path,sha256=m['sha256'],observed_period=period,filters=filters,use=use))
    write_csv('curated/source_register.csv',results,'collector source_url retrieved_at path sha256 observed_period filters use'.split())
    return results
