"""Exploratory 2024 Warbond timing analysis using saved public evidence only."""
from datetime import date, timedelta
from common import number, read_csv, read_json, write_csv
from studies import score, window


def compare(content, releases, peaks):
    """Anchor on content; also start before the observed preceding patch cluster."""
    anchor = date.fromisoformat(content['release_date'])
    preceding = sorted(
        [r for r in releases if 0 <= (anchor-date.fromisoformat(r['date'])).days <= 7
         and (r['verification'].startswith('official') or r['verification'] == 'owner: approved')],
        key=lambda r: (r['date'], r['release_id']))
    cluster = date.fromisoformat(preceding[0]['date']) if preceding else anchor
    base = score(anchor, 14, peaks, max(peaks))
    alternative = score(cluster, 14, peaks, max(peaks))
    result = dict(content, **base)
    result.update(
        preceding_patch_ids=' | '.join(r['release_id'] for r in preceding),
        preceding_patch_dates=' | '.join(r['date'] for r in preceding),
        cluster_anchor=cluster,
        cluster_to_content_days=(anchor-cluster).days,
        cluster_baseline_avg=alternative['baseline_avg'],
        cluster_short_term_lift_pct=alternative['short_term_lift_pct'],
        cluster_sustained_lift_pct=alternative['sustained_lift_pct'],
        cluster_activity_status=alternative['activity_status'])
    for label, start, end in [('week1', 0, 6), ('week2', 7, 13), ('week3', 14, 20)]:
        value, n, status = window(peaks, anchor+timedelta(days=start), anchor+timedelta(days=end), max(peaks))
        result[label+'_avg'] = value
        result[label+'_n'] = n
        result[label+'_status'] = status
        result[label+'_lift_pct'] = value/base['baseline_avg']-1 if value is not None and base['baseline_avg'] is not None and base['baseline_avg'] > 0 else None
    return result


def build():
    contents = read_csv('inputs/content_releases_2024.csv')
    assert len({r['content_id'] for r in contents}) == len(contents), 'Duplicate content IDs'
    news = {r['news_id']: r for r in read_csv('curated/news.csv')}
    for content in contents:
        entry = news[content['news_id']]
        assert entry['official'] == 'True' and entry['date'] == content['announcement_date']
        assert entry['source_path'] == content['source_path'] and entry['source_url'] == content['source_url']
        item = next(r for r in read_json(content['source_path'])['appnews']['newsitems'] if r['gid'] == content['news_id'])
        assert content['date_evidence'] in item['contents'], 'Release-date evidence changed'
    peaks = {date.fromisoformat(r['date']): number(r['steam_peak_concurrent_players']) for r in read_csv('curated/players.csv')}
    releases = read_csv('curated/releases.csv')
    results = [compare(c, releases, peaks) for c in contents]
    write_csv('outputs/content_timing_scorecard.csv', results, list(results[0]))
    sensitivity = []
    for c in contents:
        for n in (7, 28):
            sensitivity.append(dict(content_id=c['content_id'], name=c['name'], anchor_date=c['release_date'],
                **score(date.fromisoformat(c['release_date']), n, peaks, max(peaks))))
    write_csv('outputs/content_timing_sensitivity.csv', sensitivity, list(sensitivity[0]))
    events = read_csv('curated/events.csv')
    timeline = []
    for c in contents:
        anchor = date.fromisoformat(c['release_date'])
        for offset in range(-28, 36):
            day = anchor+timedelta(days=offset)
            names = [e['event_name'] for e in events if e['date'] == str(day)]
            names += [x['name']+' (Warbond release)' for x in contents if x['release_date'] == str(day)]
            timeline.append(dict(content_id=c['content_id'], date=day, relative_day=offset,
                steam_peak_concurrent_players=peaks.get(day), event_names=' | '.join(names)))
    write_csv('outputs/content_timing_timeline.csv', timeline, list(timeline[0]))
    chart(results, contents, releases, peaks)
    for r in results:
        print(r['name'], 'gap', r['cluster_to_content_days'], 'launch', r['short_term_lift_pct'], 'later', r['sustained_lift_pct'], 'cluster later', r['cluster_sustained_lift_pct'])
    return results


def chart(results, contents, releases, peaks):
    from analyze import setup, finish, INK, TEAL, GOLD, MUTED
    import matplotlib.pyplot as plt
    setup()
    fig, axes = plt.subplots(4, 2, figsize=(12, 12))
    fig.subplots_adjust(left=.085, right=.97, bottom=.10, top=.88, hspace=.68, wspace=.23)
    for ax, r in zip(axes.flat, results):
        anchor = date.fromisoformat(r['release_date'])
        base = r['baseline_avg']
        x = list(range(-14, 36))
        values = [peaks.get(anchor+timedelta(days=i)) for i in x]
        y = [v/base*100 if v is not None and base and base > 0 else float('nan') for v in values]
        ax.axvspan(22, 35, color='#BEDBD7', alpha=.45)
        ax.axhline(100, color=MUTED, linewidth=.7, linestyle='--')
        ax.axvline(0, color=TEAL, linewidth=1.4)
        ax.plot(x, y, color=INK, linewidth=1.5)
        for release in releases:
            offset = (date.fromisoformat(release['date'])-anchor).days
            if -14 <= offset <= 35 and release['verification'].startswith('official'):
                ax.plot(offset, .03, '|', color=GOLD, markersize=10, transform=ax.get_xaxis_transform())
        for content in contents:
            offset = (date.fromisoformat(content['release_date'])-anchor).days
            if -14 <= offset <= 35:
                ax.plot(offset, .09, 'v', color=TEAL, markersize=4, transform=ax.get_xaxis_transform())
        later = r['sustained_lift_pct']
        label = f'later {later:+.0%}' if later is not None else 'later unavailable'
        ax.set_title(f"{r['name']} · {r['release_date']}\n{label}", loc='left', fontsize=10)
        ax.set_xlim(-14, 35)
        ax.set_ylim(bottom=0)
        ax.set_xticks([-14, 0, 14, 28, 35])
        ax.grid(axis='y', alpha=.15)
    for ax in axes[:, 0]: ax.set_ylabel('Daily peak index')
    for ax in axes[-1, :]: ax.set_xlabel('Days from Warbond release')
    fig.text(.085, .915, 'Prior 14-day average = 100 · panel scales vary · shaded area = days 22–35', fontsize=10, color=MUTED)
    finish(fig, 'content_timing_2024.png', 'Release timing: eight 2024 Warbonds in context',
           'Teal line = Warbond anchor; triangles = Warbonds; gold ticks = official versioned patches, including hotfixes.\n'
           'Sources: saved official Steam announcements and manual SteamDB export. Scheduled dates unless availability stated.\n'
           'Exploratory, Steam-only comparison. Overlapping windows and different content prevent causal attribution.')


if __name__ == '__main__':
    build()
