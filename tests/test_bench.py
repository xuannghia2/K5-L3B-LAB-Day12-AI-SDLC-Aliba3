"""Bench statistics use slowest frame durations, not an interpolated FPS percentile."""

import math
import unittest

from chonoi.bench import summarize


class BenchStatistics(unittest.TestCase):
    def test_slowest_one_percent_uses_mean_duration_then_inverse(self):
        times = [1 / 60] * 198 + [0.1, 0.2]
        result = summarize(times, sum(times), 2400)
        self.assertEqual(set(result), {"avg_fps", "p1_low_fps", "frames", "measured_s", "load_ms"})
        self.assertAlmostEqual(result["p1_low_fps"], 2 / 0.3)
        self.assertAlmostEqual(result["avg_fps"], 200 / sum(times))
        self.assertEqual(result["frames"], 200)
        self.assertEqual(result["load_ms"], 2400)

    def test_ceil_for_101_frames_selects_two(self):
        times = [0.01] * 99 + [0.03, 0.05]
        self.assertAlmostEqual(summarize(times, sum(times), 0)["p1_low_fps"], 25)

    def test_short_run_still_uses_one_slowest_frame(self):
        self.assertAlmostEqual(summarize([0.01, 0.02], 0.03, 5)["p1_low_fps"], 50)

    def test_invalid_or_incomplete_measurements_are_rejected(self):
        for intervals, duration, load in (([], 1, 0), ([0], 1, 0), ([math.nan], 1, 0),
                ([0.01], 0, 0), ([0.01], 0.01, -1), ([0.01], 1, 0)):
            with self.subTest(intervals=intervals, duration=duration, load=load), self.assertRaises(ValueError):
                summarize(intervals, duration, load)


if __name__ == "__main__":
    unittest.main()
