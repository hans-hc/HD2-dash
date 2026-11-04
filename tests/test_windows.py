"""Boundary checks use isolated illustrative values, never written to evidence tables."""
import sys,unittest
from datetime import date,timedelta
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from studies import score,sentiment,assessment
class Windows(unittest.TestCase):
    def setUp(self):
        self.anchor=date(2024,6,13)
        self.days={self.anchor+timedelta(days=i):100.0 for i in range(-28,36)}
        self.end=max(self.days)
    def test_edges_and_missing_followup(self):
        self.days[self.anchor+timedelta(days=3)]=150
        self.days[self.anchor+timedelta(days=4)]=10000
        self.days[self.anchor+timedelta(days=35)]=None
        s=score(self.anchor,14,self.days,self.end)
        self.assertEqual(s['short_term_lift_pct'],.5);self.assertIsNone(s['sustained_lift_pct']);self.assertEqual(s['later_n'],13)
    def test_zero_baseline_and_immature(self):
        for d in self.days:
            if d<self.anchor:self.days[d]=0
        s=score(self.anchor,14,{d:v for d,v in self.days.items() if d<=self.anchor+timedelta(days=8)},self.anchor+timedelta(days=8))
        self.assertIsNone(s['short_term_lift_pct']);self.assertIn('pending',s['later_status'])
    def test_month_comparability(self):
        r={'2024-05-01':dict(completeness='complete',filter_id='a',pct_positive='.4'),'2024-06-01':dict(completeness='complete',filter_id='a',pct_positive='.6')}
        self.assertAlmostEqual(sentiment(self.anchor,r)['review_change_pp'],20)
        r['2024-06-01']['filter_id']='b';self.assertIsNone(sentiment(self.anchor,r)['review_change_pp'])
        r['2024-06-01'].update(filter_id='a',completeness='partial');self.assertIsNone(sentiment(self.anchor,r)['review_change_pp'])
    def test_human_threshold(self):
        r={'short_term_lift_pct':.2,'confounder_count':1}
        h=dict(hypothesis='',metric='short_term_lift_pct',expected_direction='increase',threshold='10',date_recorded='2026-11-03')
        self.assertEqual(assessment(h,r),('',''));h['hypothesis']='Illustrative test'
        self.assertEqual(assessment(h,r)[0],'Confounded');h['threshold']='25';self.assertEqual(assessment(h,r)[0],'Not supported')
if __name__=='__main__':unittest.main()
