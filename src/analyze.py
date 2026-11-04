"""Export scorecards and publication figures from curated evidence."""
from common import *
from studies import study_outputs
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter,PercentFormatter

CHARTS=ROOT/'outputs/charts'
INK='#192C39'; TEAL='#087A78'; GOLD='#C58A13'; ORANGE='#AD4B30'; MUTED='#536573'
COLORS={'june_2024':'#237F83','september_2024':'#A06415','psn_2024':'#9D5168'}

def setup():
    CHARTS.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':10,'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,
        'axes.edgecolor':'#B6C4C9','axes.labelcolor':INK,'xtick.color':MUTED,'ytick.color':MUTED,'axes.titlesize':14,'axes.titleweight':'bold','figure.facecolor':'#FCFCF9','axes.facecolor':'#FCFCF9','savefig.facecolor':'#FCFCF9'})

def finish(fig,name,title,footer):
    fig.suptitle(title,x=.085,y=.96,ha='left',fontweight='bold',fontsize=16,color=INK)
    fig.text(.085,.025,footer,fontsize=8,color=MUTED,va='bottom')
    fig.savefig(CHARTS/name,dpi=180);plt.close(fig)

def player_chart(main):
    data=read_csv('curated/players.csv')
    if not any(p['steam_peak_concurrent_players'] for p in data):return
    fig,ax=plt.subplots(figsize=(11,5.2));fig.subplots_adjust(left=.085,right=.97,bottom=.21,top=.77)
    dates=[date.fromisoformat(p['date']) for p in data]
    def series(k):return [number(p[k]) if p[k]!='' else float('nan') for p in data]
    ax.plot(dates,series('steam_peak_concurrent_players'),color='#82BDBD',lw=1,label='Daily peak')
    ax.plot(dates,series('steam_peak_7d_mean'),color=INK,lw=1.8,label='7-day mean')
    if any(p['sampled_max_concurrent_players'] for p in data):
        ax.plot(dates,series('sampled_max_concurrent_players'),color=ORANGE,lw=1.2,ls=':',label='Sampled maximum')
    for row in main:
        dt=row['anchor_date']; ax.axvline(dt,color=COLORS[row['case_id']],lw=1,alpha=.8)
        ax.text(dt,.985,{'psn_2024':'May','june_2024':'Jun','september_2024':'Sep'}[row['case_id']],transform=ax.get_xaxis_transform(),ha='center',va='top',color=COLORS[row['case_id']],fontsize=8,bbox=dict(facecolor='#FCFCF9',edgecolor='none',pad=1))
    ax.set_ylabel('Steam peak concurrent players');ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f'{v/1000:.0f}k'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4));ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.set_ylim(bottom=0);ax.grid(axis='y',alpha=.18);ax.legend(loc='upper right',frameon=False,ncol=3)
    finish(fig,'historical_peaks.png','Steam activity from launch through the latest complete UTC day','Source: manual SteamDB export, app 553850. Daily chart rollups and recent sampled maxima are distinct. Steam only · unofficial.')

def review_chart():
    rows=[r for r in read_csv('curated/reviews.csv') if r['completeness']=='complete']
    if not rows:return
    fig,(ax,bx)=plt.subplots(2,1,figsize=(11,6),sharex=True,gridspec_kw={'height_ratios':[1.5,1]})
    fig.subplots_adjust(left=.095,right=.97,bottom=.18,top=.83,hspace=.20)
    d=[date.fromisoformat(r['period_start']) for r in rows];p=[int(r['positive']) for r in rows];n=[int(r['negative']) for r in rows]
    ax.bar(d,p,width=23,color=TEAL,label='Positive');ax.bar(d,n,bottom=p,width=23,color=ORANGE,label='Negative')
    ax.legend(loc='upper right',ncol=2,frameon=False);ax.set_ylabel('Review count');ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f'{v/1000:.0f}k'))
    bx.plot(d,[number(r['pct_positive']) for r in rows],color=INK,lw=1.8,marker='o',ms=3);bx.set_ylim(0,1.03);bx.yaxis.set_major_formatter(PercentFormatter(1));bx.set_ylabel('Positive share')
    bx.xaxis.set_major_locator(mdates.MonthLocator(interval=4));bx.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    for a in (ax,bx):a.grid(axis='y',alpha=.17);a.set_axisbelow(True)
    finish(fig,'monthly_reviews.png','Review volume and positive share tell different stories','Source: Steam review histogram, app 553850. Complete monthly rollups only. Positive share = positive / total. Self-selected Steam reviews.')

def case_charts(main,timeline):
    for row in main:
        case=row['case_id'];data=[r for r in timeline if r['case_id']==case]
        fig,ax=plt.subplots(figsize=(10,4.7));fig.subplots_adjust(left=.095,right=.96,bottom=.23,top=.78)
        y=[r['steam_peak_concurrent_players'] for r in data]
        ax.plot([r['relative_day'] for r in data],y,color=INK,lw=2)
        for l,h,color,label in [(-14,-1,'#D6E2E4','Baseline'),(0,3,'#F4D996','Launch'),(22,35,'#BEDBD7','Later')]:
            ax.axvspan(l-.5,h+.5,color=color,alpha=.65,label=label)
        ax.axvline(0,color=GOLD,lw=1.2)
        if case=='psn_2024':ax.axvline(3,color=ORANGE,ls=':',label='Reversal (+3)')
        ax.set_xlabel('Days relative to '+str(row['anchor_date']));ax.set_ylabel('Steam peak concurrent players')
        ax.set_xlim(-28,35);ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f'{v/1000:.0f}k'))
        ax.legend(loc='upper right',ncol=4,frameon=False,fontsize=8);ax.set_ylim(bottom=0);ax.grid(axis='y',alpha=.16)
        if not any(v is not None for v in y): ax.text(.5,.5,'Daily peak observations unavailable',ha='center',transform=ax.transAxes)
        finish(fig,case+'_timeline.png',next(c['label'] for c in CASES if c['case_id']==case)+'  |  activity around the anchor','Source: manual SteamDB daily rollups. Shaded periods define the comparisons. Nearby events appear in the scorecard. Steam only · unofficial.')

def scatter(main):
    rows=[r for r in main if r['short_term_lift_pct'] is not None and r['sustained_lift_pct'] is not None]
    if len(rows)<2:return
    fig,ax=plt.subplots(figsize=(8.8,5));fig.subplots_adjust(left=.12,right=.96,bottom=.23,top=.82)
    ax.axhline(0,color='#83969A',lw=.8);ax.axvline(0,color='#83969A',lw=.8)
    for r in rows:
        x,y=r['short_term_lift_pct'],r['sustained_lift_pct']
        ax.scatter(x,y,s=100,color=COLORS[r['case_id']],zorder=3)
        label=next(c['label'] for c in CASES if c['case_id']==r['case_id'])
        below=r['case_id']=='psn_2024'
        ax.annotate(f'{label}\n{x:+.0%} short  /  {y:+.0%} later',(x,y),xytext=(0,-8 if below else 8),textcoords='offset points',ha='center',va='top' if below else 'bottom',fontsize=9)
    ax.margins(x=.29,y=.32);ax.xaxis.set_major_formatter(PercentFormatter(1));ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.set_xlabel('Short-term lift (days 0–3 maximum vs. baseline mean)')
    ax.set_ylabel('Sustained lift (days 22–35 mean vs. baseline mean)')
    positive=[r['case_id'] for r in rows if r['sustained_lift_pct']>0]
    title='Only September stayed above baseline in the later window' if len(rows)==3 and positive==['september_2024'] else 'Launch spikes and activity one month later'
    finish(fig,'lift_comparison.png',title,'Source: manual SteamDB daily rollups. Baseline = prior 14 days. Purposefully selected cases; descriptive associations.')

def main():
    main,sensitivity,timeline=study_outputs()
    for name,rows in [('impact_scorecard',main),('sensitivity_checks',sensitivity),('case_timeline',timeline)]:
        write_csv('outputs/'+name+'.csv',rows,list(rows[0]))
    setup()
    # Remove stale exported evidence charts when a rerun loses its inputs.
    for name in ['historical_peaks','monthly_reviews','lift_comparison']+[c['case_id']+'_timeline' for c in CASES]:
        (CHARTS/(name+'.png')).unlink(missing_ok=True)
    player_chart(main);review_chart();case_charts(main,timeline);scatter(main)
    for r in main:print(r['case_id'],r['activity_status'],r['short_term_lift_pct'],r['sustained_lift_pct'],r['review_change_pp'])

if __name__=='__main__':main()
