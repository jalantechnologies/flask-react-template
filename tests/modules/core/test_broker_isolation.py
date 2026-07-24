from modules.core.jobs.health_check_job import HealthCheckJob
from tests.conftest import broker_queue_depth

DEFAULT_QUEUE = "default"


class TestGivenTheBrokerIsPurgedBetweenTests:
    class TestWhenATaskIsEnqueued:
        def test_then_the_queue_holds_exactly_one_message(self) -> None:
            HealthCheckJob.perform_async()

            assert broker_queue_depth(DEFAULT_QUEUE) == 1

    class TestWhenTheNextTestRuns:
        def test_then_the_queue_starts_empty(self) -> None:
            assert broker_queue_depth(DEFAULT_QUEUE) == 0
