"""Checks for baseline contamination and complete follow-up in timing analysis."""
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from content_timing import compare


class ContentTiming(unittest.TestCase):
    def test_cluster_uses_earliest_official_patch_within_seven_days(self):
        anchor = date(2024, 9, 19)
        peaks = {anchor+timedelta(days=i): 100 for i in range(-40, 36)}
        peaks[anchor-timedelta(days=2)] = 200
        releases = [dict(date=str(anchor-timedelta(days=i)), release_id=str(i), verification=v)
                    for i, v in [(8, 'official post'), (6, 'wiki only'), (2, 'official post'), (1, 'official post')]]
        row = compare(dict(release_date=str(anchor)), releases, peaks)
        self.assertEqual(row['cluster_to_content_days'], 2)
        self.assertEqual(row['preceding_patch_ids'], '2 | 1')
        self.assertEqual(row['cluster_baseline_avg'], 100)
        self.assertGreater(row['baseline_avg'], 100)

    def test_missing_later_observation_does_not_become_zero_lift(self):
        anchor = date(2024, 6, 13)
        peaks = {anchor+timedelta(days=i): 100 for i in range(-40, 36)}
        peaks[anchor+timedelta(days=35)] = None
        row = compare(dict(release_date=str(anchor)), [], peaks)
        self.assertIsNone(row['sustained_lift_pct'])
        self.assertIsNone(row['cluster_sustained_lift_pct'])
        self.assertEqual(row['week1_lift_pct'], 0)
        self.assertEqual(row['later_n'], 13)


if __name__ == '__main__':
    unittest.main()
