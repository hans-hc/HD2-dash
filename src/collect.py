"""Collect permitted public sources. Cached by URL; --refresh adds immutable snapshots."""
from __future__ import annotations
import argparse
import json
import time
import uuid
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlencode, urljoin
import requests
from common import ROOT, LAUNCH, now, sha, jsonl, append_jsonl, write_json, sources_md, init_inputs

USER_AGENT = 'HD2-PM-Portfolio/1.0 (independent educational research; cached requests; github.com/hans-hc/HD2-dash)'
NEWS = 'https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/'
REVIEWS = 'https://store.steampowered.com/appreviewhistogram/553850?l=english'
PATCHES = [
    'https://helldivers.wiki.gg/wiki/Game_Version',
    'https://helldivers.wiki.gg/api.php?action=parse&page=Game_Version&prop=text&format=json',
]

class Fetcher:
    def __init__(self, refresh=False):
        self.refresh = refresh
        self.last_request = 0.0
        self.session = requests.Session()
        self.session.headers['User-Agent'] = USER_AGENT

    def get(self, url, collector, expect_json=True):
        if not self.refresh:
            matches = [s for s in jsonl('raw/source_manifest.jsonl') if s['url'] == url]
            if matches:
                s = matches[-1]
                if sha(ROOT / s['path']) != s['sha256']:
                    raise ValueError(f"Evidence checksum changed: {s['path']}")
                return s
            failed = [s for s in jsonl('raw/access_failures.jsonl') if s['url'] == url]
            if failed:
                print(f'WARN cached access failure: {url}; use --refresh to retry')
                return None
        for attempt in range(3):
            try:
                target=url
                for _ in range(8):
                    time.sleep(max(0,1.05-(time.monotonic()-self.last_request)))
                    self.last_request=time.monotonic()
                    r=self.session.get(target,timeout=40,allow_redirects=False)
                    if not r.is_redirect:break
                    target=urljoin(target,r.headers['Location'])
                else:
                    raise ValueError('Redirect limit exceeded')
                r.raise_for_status()
                if expect_json:
                    body = r.json()
                    if body.get('success') in (0, False) or 'error' in body:
                        raise ValueError('API reported unsuccessful response')
                stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
                path = ROOT / 'raw' / collector / (stamp + '_' + uuid.uuid4().hex[:8] + ('.json' if expect_json else '.html'))
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open('xb') as f:
                    f.write(r.content)
                entry = dict(collector=collector, url=url, retrieved_at=now(), path=str(path.relative_to(ROOT)),
                    sha256=sha(path), bytes=len(r.content), status_code=r.status_code,
                    content_type=r.headers.get('Content-Type', ''), final_url=r.url, user_agent=USER_AGENT,
                    request_filters={'l': 'english', 'review_language': 'unknown', 'off_topic': 'unknown'} if collector == 'reviews' else {},
                    coverage='See curated/coverage.json; raw response preserved without inference')
                append_jsonl('raw/source_manifest.jsonl', entry)
                print(f"SAVED {collector}: {entry['path']} ({entry['bytes']} bytes)")
                return entry
            except (requests.RequestException, ValueError) as exc:
                response = getattr(exc, 'response', None)
                code = response.status_code if response is not None else None
                append_jsonl('raw/access_failures.jsonl', dict(collector=collector, url=url, retrieved_at=now(), attempt=attempt+1, status_code=code, error=str(exc)))
                retry = code in (429, 500, 502, 503, 504) or isinstance(exc, (requests.Timeout, requests.ConnectionError))
                if not retry or attempt == 2:
                    print(f'WARN {collector}: {exc}')
                    return None
                retry_after = response.headers.get('Retry-After') if response is not None else None
                delay = 2 ** (attempt+1)
                if retry_after:
                    try:
                        delay = max(delay, float(retry_after))
                    except ValueError:
                        delay = max(delay, (parsedate_to_datetime(retry_after) - datetime.now(timezone.utc)).total_seconds())
                if delay > 60:
                    print('WARN Retry-After exceeds 60 seconds; defer collection rather than retry too soon')
                    return None
                time.sleep(delay)

def collect_news(fetch, max_pages):
    cursor = None
    pages, seen = [], set()
    boundary, reason = None, 'page_limit'
    for _ in range(max_pages):
        params = dict(appid=553850, count=100, maxlength=0, format='json')
        if cursor is not None:
            params['enddate'] = cursor
        entry = fetch.get(NEWS + '?' + urlencode(params), 'news')
        if not entry:
            reason = 'access_failure'; break
        body = json.loads((ROOT / entry['path']).read_text())['appnews']
        items = body.get('newsitems', [])
        pages.append(entry['path'])
        if not items:
            reason = 'source_exhausted'; break
        oldest = min(x['date'] for x in items)
        boundary = datetime.fromtimestamp(oldest, timezone.utc).date().isoformat()
        fresh = {x['gid'] for x in items} - seen
        seen |= {x['gid'] for x in items}
        if not fresh:
            reason = 'pagination_stalled'; break
        if boundary <= LAUNCH.isoformat():
            reason = 'reached_launch'; break
        # enddate is inclusive in practice; minus one prevents repeating the last item.
        # A page consisting entirely of one timestamp cannot safely be paginated.
        if len(items) == 100 and all(x['date'] == oldest for x in items):
            reason = 'timestamp_tie_boundary'; break
        cursor = oldest - 1
    index=dict(pages=pages, oldest_date=boundary, stop_reason=reason, unique_items=len(seen), pagination_caveat='A >100-item tie at a page boundary is not ruled out by this API.')
    previous=ROOT/'raw/news_index.json'
    if reason=='access_failure' and previous.exists():
        print('WARN refresh incomplete; retaining previous active news snapshot')
    else:
        write_json('raw/news_index.json',index)
    print(f'NEWS: {len(seen)} unique IDs; oldest {boundary}; {reason}')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('collectors', nargs='+', choices=['reviews', 'patches', 'news'])
    parser.add_argument('--refresh', action='store_true')
    parser.add_argument('--max-pages', type=int, default=150)
    args = parser.parse_args()
    init_inputs()
    from manual import register
    register()
    fetch = Fetcher(args.refresh)
    for collector in dict.fromkeys(args.collectors):
        if collector == 'news':
            collect_news(fetch, args.max_pages)
        elif collector == 'reviews':
            result = fetch.get(REVIEWS, 'reviews')
            if result:
                write_json('raw/reviews_index.json', result)
        else:
            results = [fetch.get(url, 'patches', expect_json=('api.php' in url)) for url in PATCHES]
            if any(results) or not (ROOT/'raw/patches_index.json').exists():
                write_json('raw/patches_index.json', {'responses': [r for r in results if r]})
            fetch.get('https://helldivers.wiki.gg/api.php?action=parse&page=1.001.101&prop=text&format=json', 'patch_crosscheck')
            for gid in ('6890025005348276470','6250522009530732352','5766372999945329774'):
                fetch.get('https://steamstore-a.akamaihd.net/news/externalpost/steam_community_announcements/'+gid,'anchor_pages',False)
            fetch.get('https://www.notebookcheck.net/This-community-driven-extraction-shooter-has-pulled-ahead-of-FPS-favorites-Battlefield-6-Helldivers-2-on-Steam.1159828.0.html','benchmark',False)
    sources_md()

if __name__ == '__main__':
    main()
