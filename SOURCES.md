# Sources and evidence register

Compiled from `raw/source_manifest.jsonl`, `raw/access_failures.jsonl` and curation coverage. Retrieval time is distinct from observation time. Snapshots are immutable. Public data is Steam-only; this is unofficial external analysis.

See [source register](curated/source_register.csv) for per-response observed coverage, filter metadata, resolved links and usage. Generic events-page probes are excluded from analysis.

## Current coverage

```json
{
  "calendar_start": "2024-02-08",
  "calendar_end": "2026-11-03",
  "players": {
    "status": "Reviewed chart-format inference",
    "daily_peak_start": "2024-02-08",
    "daily_peak_end": "2026-10-04",
    "header": [
      "DateTime",
      "Players",
      "Average Players"
    ],
    "raw_time_range": [
      "2017-08-14 00:00:00",
      "2026-11-04 02:30:00"
    ],
    "sha256": "704a5be2741816d01b2662bbd18bdb0bb37088869cee3d7e9c64a9e34c4c53d6",
    "daily_peak_basis": "970 paired midnight buckets; peak >= supplied average throughout; record-day bucket = 458709. Midnight is a date label, not the instant of the record.",
    "timezone": "No offset in CSV. UTC chart-day interpretation inferred from the known UTC peak date and last sample versus export time. Owner should confirm chart timezone.",
    "intraday_policy": "Subdaily values kept separately as sampled maxima. No daily-peak substitution.",
    "calendar_days_by_method": {
      "daily chart rollup": 970,
      "sampled maximum only": 30
    }
  },
  "reviews": {
    "status": "Histogram available",
    "raw_start": "2024-02-08",
    "raw_end": "2026-11-04",
    "rollup_type": "month",
    "raw_arrays": {
      "rollups": 34,
      "weeks": 0,
      "recent": 30
    },
    "complete_months": 32,
    "filter_id": "count_all_reviews=false; language=unknown; off_topic=unknown",
    "metadata": {
      "success": 1,
      "count_all_reviews": false,
      "expand_graph": false
    },
    "recent_start": "2026-10-06",
    "recent_end": "2026-11-04"
  },
  "timeline": {
    "news_items": 825,
    "official_posts": 169,
    "oldest_news": "2023-09-14",
    "newest_news": "2026-11-03",
    "pagination": "reached_launch",
    "wiki_versions_parsed": 99,
    "normalized_releases": 101,
    "events": 192
  }
}
```

## Saved successful responses

| Collector | Retrieved UTC | Evidence path | Source | SHA-256 |
|---|---|---|---|---|
| reviews | 2026-11-04T02:34:36+00:00 | `raw/reviews/20261104T023436104491Z_b599181a.json` | [source](https://store.steampowered.com/appreviewhistogram/553850?l=english) | `185187066790ada198f465a5068d94e0a23ff4f847f515dea5fe870579853310` |
| patches | 2026-11-04T02:34:37+00:00 | `raw/patches/20261104T023437080090Z_60850695.html` | [source](https://helldivers.wiki.gg/wiki/Game_Version) | `9f98f07f10b71e2a48c32db96c49823614f5affdb113518bfcf0ff5b1a91aa7b` |
| patches | 2026-11-04T02:34:38+00:00 | `raw/patches/20261104T023438715277Z_6ca384fe.json` | [source](https://helldivers.wiki.gg/api.php?action=parse&page=Game_Version&prop=text&format=json) | `362cc47a855ff120fe8ae0e7dc94283f9dcb09421fd50d51a990a22132b16d07` |
| news | 2026-11-04T02:34:39+00:00 | `raw/news/20261104T023439842215Z_9a54f7fe.json` | [source](https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=553850&count=100&maxlength=0&format=json) | `2ce2df8872073bad4a344fbca61e938718c78771eb60bcf1f3f995bc4fa724d2` |
| news | 2026-11-04T02:34:40+00:00 | `raw/news/20261104T023440429808Z_c30d407d.json` | [source](https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=553850&count=100&maxlength=0&format=json&enddate=1764688242) | `5f4944c73689b601206eebccd25dc2e72057b0c66d9b892c796b1e0fd85f0261` |
| news | 2026-11-04T02:34:41+00:00 | `raw/news/20261104T023441493064Z_f377916c.json` | [source](https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=553850&count=100&maxlength=0&format=json&enddate=1747731623) | `c662a15e2b059392ea965b44d23f0eefb2c428352b1f78f6e04d744c96912455` |
| news | 2026-11-04T02:34:42+00:00 | `raw/news/20261104T023442537090Z_e2a37a3f.json` | [source](https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=553850&count=100&maxlength=0&format=json&enddate=1735899404) | `d93ed988afa39c4a7d925ee009c8fbd4e982242b9dd74712c02c60a01995fbaf` |
| news | 2026-11-04T02:34:43+00:00 | `raw/news/20261104T023443583653Z_e59cee6f.json` | [source](https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=553850&count=100&maxlength=0&format=json&enddate=1726063934) | `6cb017fc550fa8bdc8efcd47df0ed944a32affe0b5db6a181217dc5c9fb5902a` |
| news | 2026-11-04T02:34:44+00:00 | `raw/news/20261104T023444556155Z_40ada5d5.json` | [source](https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=553850&count=100&maxlength=0&format=json&enddate=1718283428) | `a529db23c9e662ade27813302264a2fc340893e9e76feccf2419153a4e346bf8` |
| news | 2026-11-04T02:34:45+00:00 | `raw/news/20261104T023445803567Z_61632c3f.json` | [source](https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=553850&count=100&maxlength=0&format=json&enddate=1714224029) | `ebb9d749852681018bbe8cdbbf3f5321d16a1ebf8d7d80172de56e5ec8543437` |
| news | 2026-11-04T02:34:46+00:00 | `raw/news/20261104T023446693581Z_0c46b354.json` | [source](https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=553850&count=100&maxlength=0&format=json&enddate=1710067306) | `9db8f75cd0b7cbbb138761b787dd136cd4b37eafcfb6fbe584363f7b52993510` |
| news | 2026-11-04T02:34:47+00:00 | `raw/news/20261104T023447650679Z_cc41f4a8.json` | [source](https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=553850&count=100&maxlength=0&format=json&enddate=1707819403) | `bc914088372de01b6d12f71aa842a2e3749b25f5ede6beac7b258c879ce581ac` |
| players_manual | 2026-11-04T02:40:42+00:00 | `raw/manual/704a5be2741816d01b2662bbd18bdb0bb37088869cee3d7e9c64a9e34c4c53d6.csv` | [source](https://steamdb.info/app/553850/charts/) | `704a5be2741816d01b2662bbd18bdb0bb37088869cee3d7e9c64a9e34c4c53d6` |
| official_pages | 2026-11-04T02:43:00+00:00 | `raw/official_pages/20261104T024300445589Z_081f68cb.html` | [source](https://steamcommunity.com/games/553850/announcements/detail/6890025005348276470) | `a8a7259872a972954ffc6bd4bac22b49b831861ea0d291f457930121a210537b` |
| official_pages | 2026-11-04T02:43:01+00:00 | `raw/official_pages/20261104T024301599145Z_301b0c4b.html` | [source](https://steamcommunity.com/games/553850/announcements/detail/6250522009530732352) | `3af8988b77025978044274aa3c106ca8d04099e9e3ff10389b9512e2705c4605` |
| official_pages | 2026-11-04T02:43:02+00:00 | `raw/official_pages/20261104T024302584947Z_96dc9a0d.html` | [source](https://steamcommunity.com/games/553850/announcements/detail/5766372999945329774) | `71152f453d14a1f362d93f682f76a9c836b9af3c9b57b9aad746db598b29c45e` |
| patch_crosscheck | 2026-11-04T02:45:04+00:00 | `raw/patch_crosscheck/20261104T024504007026Z_c6eb5f3d.json` | [source](https://helldivers.wiki.gg/api.php?action=parse&page=1.001.101&prop=text&format=json) | `3320b81649609d8e7b3059bc1e138a554f6b99f0732f0bfdf41c7127f76ee581` |
| anchor_pages | 2026-11-04T02:45:34+00:00 | `raw/anchor_pages/20261104T024534421061Z_0cdea014.html` | [source](https://steamstore-a.akamaihd.net/news/externalpost/steam_community_announcements/6890025005348276470) | `bb3446c46a3cf65ed69f034699347676bee936acf4fe88ac47111d049622ff47` |
| anchor_pages | 2026-11-04T02:45:35+00:00 | `raw/anchor_pages/20261104T024535489807Z_717fe456.html` | [source](https://steamstore-a.akamaihd.net/news/externalpost/steam_community_announcements/6250522009530732352) | `895786980bbdc3f7ac925a75ba511103215016e19e8457e24bb2d09ad348b2f8` |
| anchor_pages | 2026-11-04T02:45:36+00:00 | `raw/anchor_pages/20261104T024536320822Z_6dedc7d7.html` | [source](https://steamstore-a.akamaihd.net/news/externalpost/steam_community_announcements/5766372999945329774) | `c6ea942d40570e06a18045acc0eef05f2db2c0ba1ac8c7d699639a5f13cda3fa` |
| benchmark | 2026-11-04T02:45:36+00:00 | `raw/benchmark/20261104T024536976453Z_fc52e47b.html` | [source](https://www.notebookcheck.net/This-community-driven-extraction-shooter-has-pulled-ahead-of-FPS-favorites-Battlefield-6-Helldivers-2-on-Steam.1159828.0.html) | `58f6bcf3e42bd5a7be0e78bb5057a29d126b8dfc73f1b043fd519522e9d4134e` |

## Access failures (not evidence)

| Time UTC | Source | Failure |
|---|---|---|
| 2026-11-04T02:43:00+00:00 | https://steamcommunity.com/games/553850/announcements/detail/6890025005348276470 | Returned generic events listing instead of the requested announcement. Excluded. Official redirect subsequently verified. |
| 2026-11-04T02:43:01+00:00 | https://steamcommunity.com/games/553850/announcements/detail/6250522009530732352 | Returned generic events listing instead of the requested announcement. Excluded. Official redirect subsequently verified. |
| 2026-11-04T02:43:02+00:00 | https://steamcommunity.com/games/553850/announcements/detail/5766372999945329774 | Returned generic events listing instead of the requested announcement. Excluded. Official redirect subsequently verified. |

## Interpretation of sources

- Official Steam community announcements are separated from third-party Steam news feeds by feed name. The external-URL flag describes the link, not authorship. Selected cases additionally require verified source mappings.
- Steam review histogram request uses `l=english` for interface text; review-language population is unknown unless the response explicitly says otherwise. Off-topic filtering is recorded as unknown when undocumented.
- Monthly review aggregation is allowed only for non-overlapping buckets aligned to a calendar month or a complete set of daily buckets. Cross-month buckets remain at their original resolution.
- A current review snapshot may incorporate later edits or removals. It is not a time machine for event-day sentiment.
- SteamDB is manual-only. Its raw export is excluded from Git. The reported record (458,709 on 2024-02-24) is cross-checked against the manual CSV and the saved independent benchmark article. See the validation report for the result.
- Wiki access failures do not authorize bypassing access controls. The selected-case release timeline can use official notes while the wider wiki timeline remains incomplete.
