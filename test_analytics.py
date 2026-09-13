import unittest
import pandas as pd
from analytics import load_data, prepare, batting, bowling, filter_data


class AnalyticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m, cls.d = load_data()

    def test_snapshot_and_seasons(self):
        self.assertEqual(len(self.m), 1095)
        self.assertEqual(len(self.d), 260920)
        self.assertEqual(
            sorted(self.m.season.unique()),
            list(range(2008, 2025))
        )
        self.assertEqual(
            len(self.m[self.m.match_type.eq('Final')]),
            17
        )

    def test_first_match_known_score(self):
        # McCullum's 158 off 73 in the opening IPL match is an independent control.
        p = self.d[
            self.d.match_id.eq(335982)
            & self.d.batter.eq('BB McCullum')
        ]
        stats = batting(p).iloc[0]
        self.assertEqual(stats.Runs, 158)
        self.assertEqual(stats.Balls, 73)
        self.assertEqual(stats.Sixes, 13)

    def test_extras_and_dismissal_rules(self):
        raw_m = pd.read_csv('data/matches.csv').head(1)
        row = pd.read_csv('data/deliveries.csv.gz', nrows=1)
        balls = pd.concat([row] * 4, ignore_index=True)
        balls['extras_type'] = ['wides', 'noballs', 'byes', '']
        balls['extra_runs'] = [1, 1, 4, 0]
        balls['batsman_runs'] = [0, 6, 0, 0]
        balls['total_runs'] = [1, 7, 4, 0]
        balls['dismissal_kind'] = ['', '', 'run out', 'bowled']
        _, d = prepare(raw_m, balls)
        self.assertEqual(d.ball_faced.sum(), 3)
        self.assertEqual(d.legal_ball.sum(), 2)
        self.assertEqual(d.conceded.sum(), 8)
        self.assertEqual(d.bowler_wicket.sum(), 1)
        self.assertEqual(bowling(d).iloc[0].Economy, 24)

    def test_filter_and_super_over(self):
        m, d = filter_data(
            self.m, self.d, [2024], 'Chennai Super Kings'
        )
        self.assertTrue(m.season.eq(2024).all())
        self.assertTrue(
            (
                m.team1.eq('Chennai Super Kings')
                | m.team2.eq('Chennai Super Kings')
            ).all()
        )
        self.assertTrue(d.match_id.isin(m.id).all())
        self.assertTrue(d.inning.le(2).all())
        self.assertTrue(
            filter_data(self.m, self.d, [1900])[1].empty
        )

    def test_reject_unmatched_pair(self):
        m = pd.read_csv('data/matches.csv').head(1)
        d = pd.read_csv('data/deliveries.csv.gz', nrows=1)
        d['match_id'] = -1
        with self.assertRaisesRegex(ValueError, 'matching match ID'):
            prepare(m, d)


if __name__ == '__main__':
    unittest.main()
