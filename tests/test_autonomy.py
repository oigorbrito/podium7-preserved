import unittest

from podium7.autonomy import (
    AcquisitionCache,
    Checkpoint,
    JobState,
    RateLimiter,
    RetryPolicy,
    identify_gaps,
    plan_jobs,
    run_job,
)


class AutonomyTests(unittest.TestCase):
    def test_gap_detection_is_deterministic(self):
        gaps = identify_gaps({"power", "torque", "weight"}, {"power"})
        self.assertEqual(gaps, ("torque", "weight"))

    def test_job_planning_uses_known_source(self):
        jobs = plan_jobs("entity-1", ("power",), "known-source")
        self.assertEqual(jobs[0].source_id, "known-source")
        self.assertEqual(jobs[0].attribute, "power")

    def test_retry_recovers_transient_failure(self):
        job = plan_jobs("entity-1", ("power",), "known-source")[0]
        checkpoint = Checkpoint()
        calls = {"count": 0}
        def worker(_job):
            calls["count"] += 1
            if calls["count"] == 1:
                raise RuntimeError("temporary")
            return 123
        result = run_job(job, worker, checkpoint=checkpoint, retry_policy=RetryPolicy(3))
        self.assertEqual(result.state, JobState.SUCCEEDED)
        self.assertEqual(result.attempts, 2)
        self.assertIn(job.id, checkpoint.completed_jobs)

    def test_permanent_failure_is_checkpointed(self):
        job = plan_jobs("entity-1", ("power",), "known-source")[0]
        checkpoint = Checkpoint()
        result = run_job(job, lambda _job: (_ for _ in ()).throw(RuntimeError("down")), checkpoint=checkpoint, retry_policy=RetryPolicy(2))
        self.assertEqual(result.state, JobState.FAILED)
        self.assertEqual(checkpoint.failed_attempts[job.id], 2)

    def test_rate_limit_blocks_early_repeat(self):
        limiter = RateLimiter(10.0)
        self.assertTrue(limiter.allow("source", 100.0))
        self.assertFalse(limiter.allow("source", 105.0))
        self.assertTrue(limiter.allow("source", 110.0))

    def test_cache_reuses_acquisition(self):
        cache = AcquisitionCache[str]()
        cache.put("source", "locator", "payload")
        self.assertEqual(cache.get("source", "locator"), "payload")


if __name__ == "__main__":
    unittest.main()
