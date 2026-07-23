from modules.core.workers.health_check_worker import HealthCheckWorker
from tests.conftest import broker_queue_depth

DEFAULT_QUEUE = "default"


class TestGivenTheBrokerIsPurgedBetweenTests:
    class TestWhenATaskIsEnqueued:
        def test_then_the_queue_holds_exactly_one_message(self) -> None:
            HealthCheckWorker.perform_async()

            assert broker_queue_depth(DEFAULT_QUEUE) == 1

    class TestWhenTheNextTestRuns:
        def test_then_the_queue_starts_empty(self) -> None:
            assert broker_queue_depth(DEFAULT_QUEUE) == 0
