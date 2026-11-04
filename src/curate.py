"""Curate immutable public evidence and reviewed inputs. No network operations."""
from __future__ import annotations
import calendar
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
import re
from statistics import mean
from common import *

SCHEMAS = {
    'players': 'date steam_peak_concurrent_players average_concurrent_players sampled_max_concurrent_players observation_method sample_count weekday is_weekend steam_peak_7d_mean source_path',
    'reviews': 'period_start period_end positive negative total pct_positive granularity completeness filter_id source_path',
    'review_buckets': 'series bucket_start bucket_end granularity positive negative filter_id source_path',
    'news': 'news_id published_at_utc date title feedname official external_url source_url source_path',
    'releases': 'release_id version date source_date official_name source_url summary download_size change_type_suggested scope_suggested change_type scope needs_review verification wiki_date source_path',
    'events': 'event_id case_id date event_name source_date source_name event_type release_id source_url verification source_path related_news_ids',
}

def save(name, rows):
    write_csv('curated/'+name+'.csv',rows,SCHEMAS[name].split())

def players(end):
    entry = read_json('raw/manual_index.json',{})
    observations, methods = {}, Counter()
    info = {'status': entry.get('reason','Missing manual export'), 'daily_peak_start': None, 'daily_peak_end': None}
    if entry.get('path') and (ROOT/entry['path']).exists():
        raw = read_csv(entry['path'])
        groups = defaultdict(list)
        points = set()
        try:
            for record in raw:
                stamp=datetime.fromisoformat(record['DateTime'])
                if stamp in points:
                    raise ValueError('Duplicate timestamp')
                points.add(stamp)
                if LAUNCH <= stamp.date() <= end:
                    groups[stamp.date()].append((stamp,record))
            daily = {d:v[0][1] for d,v in groups.items() if len(v)==1 and v[0][0].time()==datetime.min.time()}
            benchmark = daily.get(date(2024,2,24),{}).get('Players')
            pairs = [(int(v['Players']),int(v['Average Players'])) for v in daily.values() if v['Players'] and v['Average Players']]
            # In this inspected chart format, daily midnight buckets include a distinct
            # average. The known intraday record is assigned to its date's midnight.
            # Neither lone samples nor exports lacking this evidence pass this gate.
            dense = any(d+timedelta(days=1) in daily for d in daily)
            known_export = entry['sha256']=='704a5be2741816d01b2662bbd18bdb0bb37088869cee3d7e9c64a9e34c4c53d6'
            reviewed = read_json('inputs/player_export_review.json', {})
            declared = reviewed.get('sha256')==entry['sha256'] and reviewed.get('daily_midnight_rows')=='Steam daily peaks' and reviewed.get('timezone')=='UTC'
            eligible = dense and (declared or (known_export and len(pairs)>=7)) and all(p>=a>=0 for p,a in pairs)
            for d, series in groups.items():
                counts = [int(r['Players']) for _,r in series if r['Players']!='']
                if any(n<0 for n in counts):
                    raise ValueError('Negative player count')
                adjacent = d-timedelta(days=1) in daily or d+timedelta(days=1) in daily
                if d in daily and eligible and adjacent:
                    record=daily[d]
                    peak=int(record['Players']) if record['Players'] else None
                    avg=int(record['Average Players']) if record['Average Players'] else None
                    observations[d]=(peak,avg,None,'daily chart rollup',len(series))
                else:
                    observations[d]=(None,None,max(counts,default=None),'sampled maximum only',len(series))
            verified=[d for d,values in observations.items() if values[0] is not None]
            info.update(status='Reviewed chart-format inference' if eligible else 'No verified daily peak series',
                daily_peak_start=str(min(verified)) if verified else None, daily_peak_end=str(max(verified)) if verified else None,
                header=entry['headers'], raw_time_range=entry['coverage'], sha256=entry['sha256'],
                daily_peak_basis=f'{len(pairs)} paired midnight buckets; peak >= supplied average throughout; record-day bucket = {benchmark}. Midnight is a date label, not the instant of the record.',
                timezone='No offset in CSV. UTC chart-day interpretation inferred from the known UTC peak date and last sample versus export time. Owner should confirm chart timezone.',
                intraday_policy='Subdaily values kept separately as sampled maxima. No daily-peak substitution.')
        except (ValueError,KeyError,TypeError) as e:
            observations.clear()
            info['status']='Unsuitable export: '+str(e)
    rows=[]
    for d in days(LAUNCH,end):
        peak,avg,sampled,method,n = observations.get(d,(None,None,None,'missing',0))
        seven = [observations.get(d-timedelta(days=i),(None,))[0] for i in range(7)]
        rows.append(dict(date=d,steam_peak_concurrent_players=peak,average_concurrent_players=avg,sampled_max_concurrent_players=sampled,
            observation_method=method,sample_count=n,weekday=d.strftime('%A'),is_weekend=d.weekday()>=5,
            steam_peak_7d_mean=mean(seven) if all(v is not None for v in seven) else None,source_path=entry.get('path','') if n else ''))
        methods[method]+=1
    info['calendar_days_by_method']=dict(methods)
    save('players',rows)
    return info

def utcday(stamp):
    return datetime.fromtimestamp(stamp,timezone.utc).date()

def month_end(d):
    return d.replace(day=calendar.monthrange(d.year,d.month)[1])

def reviews(end):
    entry=read_json('raw/reviews_index.json',{})
    rows,buckets=[],[]
    info={'status':'No histogram snapshot'}
    if entry:
        body=read_json(entry['path'])
        result=body['results']
        filter_id='count_all_reviews='+str(body.get('count_all_reviews','unknown')).lower()+'; language=unknown; off_topic=unknown'
        by_month=defaultdict(list)
        rollup_type=result.get('rollup_type','unknown')
        first,last=utcday(result['start_date']),utcday(result['end_date'])
        last_complete=min(end,datetime.fromisoformat(entry['retrieved_at']).date()-timedelta(days=1),last)
        for series in ('rollups','weeks','recent'):
            grain={'rollups':rollup_type,'weeks':'week','recent':'day'}[series]
            seen=set()
            for item in result.get(series,[]):
                d=utcday(item['date'])
                if d in seen:
                    raise ValueError('Duplicate review bucket in '+series)
                seen.add(d)
                finish=month_end(d) if grain=='month' and d.day==1 else (d+timedelta(days=6) if grain=='week' else d if grain=='day' else None)
                pos,neg=item['recommendations_up'],item['recommendations_down']
                if not isinstance(pos,int) or not isinstance(neg,int) or min(pos,neg)<0:
                    raise ValueError('Invalid review counts')
                row=dict(series=series,bucket_start=d,bucket_end=finish,granularity=grain,positive=pos,negative=neg,filter_id=filter_id,source_path=entry['path'])
                buckets.append(row)
                if finish and grain in ('day','month'):
                    by_month[d.replace(day=1)].append(row)
        for m,group in sorted(by_month.items()):
            monthly=[b for b in group if b['granularity']=='month' and b['series']=='rollups']
            daily={b['bucket_start']:b for b in group if b['granularity']=='day'}
            if monthly:
                chosen=monthly
            elif set(daily)==set(days(m,month_end(m))):
                chosen=list(daily.values())
            else:
                continue
            pos=sum(b['positive'] for b in chosen); neg=sum(b['negative'] for b in chosen)
            complete=m>=max(first,LAUNCH) and month_end(m)<=last_complete
            rows.append(dict(period_start=m,period_end=month_end(m),positive=pos,negative=neg,total=pos+neg,pct_positive=pos/(pos+neg) if pos+neg else None,
                granularity='month',completeness='complete' if complete else 'partial',filter_id=filter_id,source_path=entry['path']))
        info=dict(status='Histogram available',raw_start=str(first),raw_end=str(last),rollup_type=rollup_type,
            raw_arrays={k:len(result.get(k,[])) for k in ('rollups','weeks','recent')},complete_months=sum(r['completeness']=='complete' for r in rows),
            filter_id=filter_id,metadata={k:v for k,v in body.items() if k!='results'},
            recent_start=str(min((b['bucket_start'] for b in buckets if b['series']=='recent'),default='')),recent_end=str(max((b['bucket_start'] for b in buckets if b['series']=='recent'),default='')))
    save('reviews',rows);save('review_buckets',buckets)
    return info

class VersionTable(HTMLParser):
    def __init__(self):
        super().__init__(); self.active=False; self.cell=None; self.current=[]; self.rows=[]
    def handle_starttag(self,tag,attrs):
        if tag=='table' and 'wikitable' in dict(attrs).get('class',''):
            self.active=True
        if self.active and tag=='tr': self.current=[]
        if self.active and tag=='td': self.cell=[]
    def handle_data(self,data):
        if self.cell is not None: self.cell.append(data)
    def handle_endtag(self,tag):
        if self.active and tag=='td' and self.cell is not None:
            self.current.append(''.join(self.cell).strip()); self.cell=None
        if self.active and tag=='tr' and len(self.current)==3:
            self.rows.append(self.current)
        if tag=='table': self.active=False

def version(title):
    match=re.search(r'(?<!\d)0?(\d{1,2}\.\d{3})\.(\d{1,3})(?!\d)',title)
    return match.group(1)+'.'+match.group(2).zfill(3) if match else None

def wiki():
    entries=read_json('raw/patches_index.json',{}).get('responses',[])
    for entry in sorted(entries,key=lambda e: not e['path'].endswith('.json')):
        path=entry['path']
        content=read_json(path)['parse']['text']['*'] if path.endswith('.json') else (ROOT/path).read_text()
        parser=VersionTable(); parser.feed(content)
        rows={}
        for name,size,dt in parser.rows:
            v=version(name)
            if v and re.fullmatch(r'\d{4}-\d{2}-\d{2}',dt):
                rows[v]=(dt,size,path)
        if rows: return rows
    return {}

ANCHOR_GIDS={'6890025005348276470':'june_2024','6250522009530732352':'september_2024','5766372999945329774':'psn_2024'}
JUNE,SEPT,PSN=ANCHOR_GIDS
EXTRA={
    '5746109972548721060':('2024-06-13','Viper Commandos Warbond scheduled release','June 13'),
    '6250522009513151638':('2024-09-19','Chemical Agents Warbond scheduled release','September 19'),
    '5766372999943498700':('2024-05-09','Polar Patriots Warbond scheduled release','May 9'),
}
EXPLAINS={'6890025005348276923':JUNE,'6211118320240881542':'6211118320240873195'}

def classify(text):
    terms={'Balance':r'\bbalanc|\barmor penetration|\bweapon damage', 'Stability':r'\bcrash|\bstability', 'Content':r'\bnew mission|\bnew biomes?|\bnew feature', 'Platform':r'\bcrossplay|\bplatform support'}
    matched=[k for k,p in terms.items() if re.search(p,text,re.I)]
    return (matched[0] if len(matched)==1 else 'Mixed' if matched else 'Unclassified',
            'Multi-system' if len(matched)>1 else 'Focused' if matched else 'Unknown',matched)

def timeline(end):
    index=read_json('raw/news_index.json',{})
    news={}
    bodies={}
    for path in index.get('pages',[]):
        for x in read_json(path)['appnews']['newsitems']:
            gid=x['gid']; dt=datetime.fromtimestamp(x['date'],timezone.utc)
            if gid in news: continue
            news[gid]=dict(news_id=gid,published_at_utc=dt.isoformat(),date=dt.date().isoformat(),title=x['title'],feedname=x['feedname'],
                official=x['feedname']=='steam_community_announcements',external_url=x['is_external_url'],source_url=x['url'],source_path=path)
            bodies[gid]=x['contents']
    save('news',sorted(news.values(),key=lambda x:x['published_at_utc']))
    wikirows=wiki()
    releases,events={},{}
    def add_event(eid,n,typ,dt=None,label=None,rid='',case='',status='official post'):
        day=dt or n['date']; name=label or n['title']
        events[eid]=dict(event_id=eid,case_id=case,date=day,event_name=name,source_date=day,source_name=name,event_type=typ,release_id=rid,
            source_url=n['source_url'],verification=status,source_path=n['source_path'],related_news_ids=n.get('news_id',''))
    for gid,n in sorted(news.items(),key=lambda t:t[1]['date']):
        if not n['official'] or not LAUNCH.isoformat()<=n['date']<=end.isoformat() or gid in EXPLAINS: continue
        v=version(n['title'])
        if gid=='6341720536499099567' and 'host migration' in bodies[gid] and '1.001.101' in wikirows:
            # The reviewed wiki hotfix page has the same shield and host-migration fixes.
            # Preserve the Steam title verbatim and use the cross-checked version key.
            v='1.001.101'
        if v and not re.search(r'explained|preview',n['title'],re.I):
            rid='release-'+v
            if rid in releases and releases[rid]['date']==n['date']:
                events[rid]['related_news_ids']+='|'+gid
                continue
            if rid in releases:
                rid+='-'+n['date']
            changes=re.split(r'known issues',bodies[gid],maxsplit=1,flags=re.I)[0]
            typ,scope,terms=classify(changes)
            summary={'6890025005348276470':'Rebalanced stratagems and weapons, exposed supply lines, added invite-only lobbies and addressed crashes.',
                '6250522009530732352':'Reworked armor and anti-tank interactions, weapon viability and enemy health alongside feature and stability changes.'}.get(gid)
            summary=summary or ('Published notes mention '+', '.join(terms)+'.' if terms else 'Official versioned announcement; content needs review.')
            w=wikirows.get(v,('','',''))
            releases[rid]=dict(release_id=rid,version=v,date=n['date'],source_date=n['date'],official_name=n['title'],source_url=n['source_url'],summary=summary,
                download_size=w[1],change_type_suggested=typ,scope_suggested=scope,change_type=typ,scope=scope,needs_review=True,verification='official post',wiki_date=w[0],source_path=n['source_path'])
            add_event(rid,n,'Release',rid=rid,case=ANCHOR_GIDS.get(gid,''))
        elif gid==PSN:
            add_event('psn-announcement',n,'Policy',case='psn_2024')
            if 'UPDATE 5/6/2024' in bodies[gid] and 'will not be moving forward' in bodies[gid]:
                add_event('psn-reversal',n,'Policy','2024-05-06','Account-linking requirement withdrawn',case='psn_2024',status='official dated amendment')
        elif gid in EXTRA:
            dt,name,proof=EXTRA[gid]
            if proof in bodies[gid]:
                add_event('content-'+gid,n,'Content',dt,name,status='official announced schedule')
        else:
            add_event('news-'+gid,n,'Announcement')
    for gid,other in EXPLAINS.items():
        if gid in news:
            for e in events.values():
                if e['related_news_ids']==other: e['related_news_ids']+='|'+gid; break
    for v,(dt,size,path) in wikirows.items():
        if 'release-'+v not in releases and LAUNCH.isoformat()<=dt<=end.isoformat():
            rid='release-'+v
            ref={'date':dt,'title':'Version '+v,'source_url':'https://helldivers.wiki.gg/wiki/Game_Version','source_path':path}
            releases[rid]=dict(release_id=rid,version=v,date=dt,source_date=dt,official_name='',source_url=ref['source_url'],summary='Secondary timeline only; official contents unverified.',
                download_size=size,change_type_suggested='Unclassified',scope_suggested='Unknown',change_type='Unclassified',scope='Unknown',needs_review=True,verification='wiki only',wiki_date=dt,source_path=path)
            add_event(rid,ref,'Release',rid=rid,status='wiki only')
    for review in read_csv('inputs/event_reviews.csv'):
        eid=review['event_id']
        if eid not in events: raise ValueError('Unknown reviewed event ID: '+eid)
        e=events[eid]
        if review['date_override']: e['date']=date.fromisoformat(review['date_override']).isoformat()
        if review['name_override']: e['event_name']=review['name_override']
        if review['review_status']: e['verification']='owner: '+review['review_status']
        if e['release_id']:
            r=releases[e['release_id']];r['date']=e['date']
            for dest,src in [('change_type','change_type_override'),('scope','scope_override')]:
                if review[src]:r[dest]=review[src]
            r['needs_review']=review['review_status']!='approved'
    save('releases',sorted(releases.values(),key=lambda r:r['date']))
    save('events',sorted(events.values(),key=lambda e:(e['date'],e['event_id'])))
    return dict(news_items=len(news),official_posts=sum(n['official'] for n in news.values()),oldest_news=index.get('oldest_date'),newest_news=max((n['date'] for n in news.values()),default=None),
        pagination=index.get('stop_reason'),wiki_versions_parsed=len(wikirows),normalized_releases=len(releases),events=len(events))

def main():
    init_inputs()
    end=cutoff()
    coverage=dict(calendar_start=str(LAUNCH),calendar_end=str(end),players=players(end),reviews=reviews(end),timeline=timeline(end))
    write_json('curated/coverage.json',coverage)
    from provenance import entries
    entries()
    sources_md()
    print('Curated through',end,coverage['players']['calendar_days_by_method'],coverage['reviews'].get('complete_months'), 'complete review months')

if __name__=='__main__':
    main()
