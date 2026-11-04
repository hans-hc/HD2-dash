"""Descriptive event-window calculations shared by validation and reporting."""
from datetime import date,timedelta
from statistics import mean
from common import CASES, days, number, read_csv

ANCHORS={'june_2024':'release-1.000.400','september_2024':'release-1.001.100','psn_2024':'psn-announcement'}

def window(peaks,start,end,calendar_end,func=mean):
    dates=days(start,end)
    values=[peaks[d] for d in dates if peaks.get(d) is not None]
    if len(values)==len(dates):
        return func(values),len(values),'eligible'
    if end>calendar_end: reason='pending: window not mature'
    elif start<min(peaks): reason='outside calendar'
    else: reason='missing daily peaks'
    return None,len(values),reason

def score(anchor,n,peaks,calendar_end):
    base,bc,br=window(peaks,anchor-timedelta(days=n),anchor-timedelta(days=1),calendar_end)
    short,sc,sr=window(peaks,anchor,anchor+timedelta(days=3),calendar_end,max)
    later,lc,lr=window(peaks,anchor+timedelta(days=22),anchor+timedelta(days=35),calendar_end)
    def lift(value):
        return (value-base)/base if value is not None and base is not None and base>0 else None
    return dict(baseline_days=n,baseline_n=bc,launch_n=sc,later_n=lc,baseline_status=br,launch_status=sr,later_status=lr,
        baseline_avg=base,launch_window_max=short,day22_35_avg=later,short_term_lift_pct=lift(short),sustained_lift_pct=lift(later),
        activity_status='eligible' if br==sr==lr=='eligible' and base>0 else ' / '.join([br,sr,lr,'baseline must be positive' if base==0 else '']).rstrip(' /'))

def sentiment(anchor,reviews):
    m=anchor.replace(day=1)
    current=reviews.get(str(m)); prior=reviews.get(str((m-timedelta(days=1)).replace(day=1)))
    complete=current and prior and current['completeness']==prior['completeness']=='complete' and current['filter_id']==prior['filter_id']
    valid=complete and current['pct_positive']!='' and prior['pct_positive']!=''
    return dict(review_month=m,prior_review_pct=number(prior['pct_positive']) if prior else None,
        event_review_pct=number(current['pct_positive']) if current else None,
        review_change_pp=100*(float(current['pct_positive'])-float(prior['pct_positive'])) if valid else None,
        review_status='comparable complete months' if valid else 'missing, partial, empty or incompatible month')

def assessment(h,row):
    if not h or not h['hypothesis'].strip(): return '',''
    metric=h['metric']
    if metric not in ('short_term_lift_pct','sustained_lift_pct','review_change_pp') or h['expected_direction'] not in ('increase','decrease') or not h['date_recorded']:
        return 'Inconclusive','Complete the metric, date and direction using the input guide.'
    try: threshold=float(h['threshold'])
    except (ValueError,TypeError): return 'Inconclusive','A numeric threshold is missing.'
    if threshold<0: return 'Inconclusive','Use an unsigned magnitude in percent or percentage points.'
    val=row[metric]
    if val is None: return 'Inconclusive','The required window or comparable month is missing.'
    observed=(100*val if metric.endswith('_pct') else val)
    aligned=observed if h['expected_direction']=='increase' else -observed
    matches=aligned>=threshold and aligned>0
    if row['confounder_count'] and matches: return 'Confounded','Directional threshold met; concurrent documented events prevent isolation.'
    return ('Supported','Descriptive direction and threshold met.') if matches else ('Not supported','Observed direction or magnitude misses the stated threshold.')

def study_outputs():
    players=read_csv('curated/players.csv')
    peaks={date.fromisoformat(p['date']):number(p['steam_peak_concurrent_players']) for p in players}
    events=read_csv('curated/events.csv')
    by_id={e['event_id']:e for e in events}
    reviews={r['period_start']:r for r in read_csv('curated/reviews.csv')}
    hypotheses={h['case_id']:h for h in read_csv('inputs/hypotheses.csv')}
    main,sensitivity,timeline=[],[],[]
    for c in CASES:
        case=c['case_id']; event=by_id.get(ANCHORS[case]); anchor=date.fromisoformat(event['date'] if event else c['anchor_date'])
        verified=bool(event and (event['verification'].startswith('official') or event['verification']=='owner: approved'))
        if case=='psn_2024': verified=verified and 'psn-reversal' in by_id
        nearby=[e for e in events if e['event_id']!=ANCHORS[case] and -28<=(date.fromisoformat(e['date'])-anchor).days<=35]
        def names(lo,hi):
            return ' | '.join(f"{e['date']} {e['event_name']}" for e in nearby if lo<=(date.fromisoformat(e['date'])-anchor).days<=hi)
        for n in (7,14,28):
            row=dict(case_id=case,anchor_event_id=ANCHORS[case],anchor_date=anchor,event_name=event['event_name'] if event else c['label'],
                verification='verified' if verified else 'unverified',**score(anchor,n,peaks,max(peaks)))
            if not verified:
                for k in ('baseline_avg','launch_window_max','day22_35_avg','short_term_lift_pct','sustained_lift_pct'): row[k]=None
                row['activity_status']='anchor unverified'
            row.update(baseline_events=names(-n,-1),launch_events=names(0,3),intervening_events=names(4,21),later_events=names(22,35))
            if n!=14:
                sensitivity.append(row)
            else:
                row['pre14_avg']=row.pop('baseline_avg')
                row.update(sentiment(anchor,reviews))
                if not verified: row.update(review_change_pp=None,review_status='anchor unverified')
                row['confounder_count']=sum((date.fromisoformat(e['date'])-anchor).days>=-14 for e in nearby)
                first=window(peaks,anchor-timedelta(days=14),anchor-timedelta(days=8),max(peaks))[0]
                last=window(peaks,anchor-timedelta(days=7),anchor-timedelta(days=1),max(peaks))[0]
                row['pretrend_pct']=(last-first)/first if first and last is not None else None
                row['hypothesis_assessment'],row['assessment_reason']=assessment(hypotheses.get(case),row)
                main.append(row)
        for offset in range(-28,36):
            dt=anchor+timedelta(days=offset)
            phase='extended baseline' if offset<-14 else 'baseline' if offset<0 else 'launch' if offset<=3 else 'intervening' if offset<22 else 'later'
            today=[e for e in events if e['date']==str(dt)]
            timeline.append(dict(case_id=case,date=dt,relative_day=offset,phase=phase,steam_peak_concurrent_players=peaks.get(dt),event_names=' | '.join(e['event_name'] for e in today)))
    return main,sensitivity,timeline
