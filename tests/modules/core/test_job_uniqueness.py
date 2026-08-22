import uuid
from typing import Any, Iterator, Optional, cast

import pytest

from modules.core.celery_app import app as celery_app
from modules.core.common.types import ActorType, AuditActor, JobRun, JobRunQuery, JobRunStatus
from modules.core.internal.cache.cache_client import CacheClient
from modules.core.internal.cache.cache_manager import namespaced_key
from modules.core.internal.job_run.store.job_run_repository import JobRunRepository
from modules.core.job import JOB_LOCK_KEY_PREFIX, Job
from modules.core.lock_service import LockService

JOB_LOGGER = "modules.logger.internal.console_logger"

RUN_LOG: list[str] = []
REENTRANT_ARGUMENTS: list[str] = []
LOCK_OBSERVATIONS: list[bool] = []
OBSERVED_TTLS: list[int] = []


class UniqueJob(Job):
    max_retries = 0
    unique_for_seconds = 60

    @classmethod
    def unique_key(cls, *args: Any, **kwargs: Any) -> Optional[str]:
        return str(args[0])

    @classmethod
    def perform(cls, *args: Any, actor: AuditActor, **kwargs: Any) -> str:
        argument = str(args[0])
        RUN_LOG.append(argument)
        LOCK_OBSERVATIONS.append(_lock_exists(cls.__name__, argument))
        while REENTRANT_ARGUMENTS:
            UniqueJob.perform_async(REENTRANT_ARGUMENTS.pop(0))
        return argument


class UniqueFailingJob(Job):
    max_retries = 0
    unique_for_seconds = 60

    @classmethod
    def unique_key(cls, *args: Any, **kwargs: Any) -> Optional[str]:
        return str(args[0])

    @classmethod
    def perform(cls, *args: Any, actor: AuditActor, **kwargs: Any) -> None:
        RUN_LOG.append(str(args[0]))
        raise RuntimeError("unique job body failed")


class TtlObservingJob(Job):
    max_retries = 0
    unique_for_seconds = 45

    @classmethod
    def unique_key(cls, *args: Any, **kwargs: Any) -> Optional[str]:
        return str(args[0])

    @classmethod
    def perform(cls, *args: Any, actor: AuditActor, **kwargs: Any) -> str:
        argument = str(args[0])
        OBSERVED_TTLS.append(_lock_ttl(cls.__name__, argument))
        return argument


class UnkeyedJob(Job):
    max_retries = 0

    @classmethod
    def perform(cls, *args: Any, actor: AuditActor, **kwargs: Any) -> str:
        RUN_LOG.append("unkeyed")
        return "unkeyed"


@pytest.fixture(autouse=True)
def eager_celery() -> Iterator[None]:
    previous_eager = celery_app.conf.task_always_eager
    previous_propagate = celery_app.conf.task_eager_propagates
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    yield
    celery_app.conf.task_always_eager = previous_eager
    celery_app.conf.task_eager_propagates = previous_propagate


@pytest.fixture(autouse=True)
def clean_state() -> Iterator[None]:
    RUN_LOG.clear()
    REENTRANT_ARGUMENTS.clear()
    LOCK_OBSERVATIONS.clear()
    OBSERVED_TTLS.clear()
    JobRunRepository.collection().delete_many({})
    yield
    RUN_LOG.clear()
    REENTRANT_ARGUMENTS.clear()
    LOCK_OBSERVATIONS.clear()
    OBSERVED_TTLS.clear()
    JobRunRepository.collection().delete_many({})


def _unique_argument() -> str:
    return f"key-{uuid.uuid4().hex}"


def _lock_key(job_name: str, key: str) -> str:
    return f"{JOB_LOCK_KEY_PREFIX}:{job_name}:{key}"


def _lock_exists(job_name: str, key: str) -> bool:
    return bool(CacheClient.get_client().exists(namespaced_key(_lock_key(job_name, key))))


def _lock_ttl(job_name: str, key: str) -> int:
    return cast(int, CacheClient.get_client().ttl(namespaced_key(_lock_key(job_name, key))))


def _reader_actor() -> AuditActor:
    return AuditActor(actor_type=ActorType.WORKER, actor_id="test-reader")


def _job_runs(job_name: str) -> list[JobRun]:
    return JobRunRepository.query(JobRunQuery(job_name=job_name), actor=_reader_actor())


class TestGivenAJobDeclaresAUniqueKey:
    class TestWhenASecondRunStartsWhileTheKeyIsHeld:
        def test_then_the_second_run_does_not_perform_the_work(self) -> None:
            argument = _unique_argument()
            REENTRANT_ARGUMENTS.append(argument)

            UniqueJob.perform_async(argument)

            assert RUN_LOG == [argument]

        def test_then_the_skipped_run_is_recorded_as_skipped(self) -> None:
            argument = _unique_argument()
            REENTRANT_ARGUMENTS.append(argument)

            UniqueJob.perform_async(argument)

            statuses = [run.status for run in _job_runs("UniqueJob")]
            assert sorted(statuses) == sorted([JobRunStatus.SKIPPED, JobRunStatus.SUCCEEDED])

        def test_then_the_skip_is_logged(self, caplog: pytest.LogCaptureFixture) -> None:
            argument = _unique_argument()
            REENTRANT_ARGUMENTS.append(argument)

            with caplog.at_level("INFO", logger=JOB_LOGGER):
                UniqueJob.perform_async(argument)

            assert any("Skipped job UniqueJob" in record.getMessage() for record in caplog.records)

    class TestWhenASecondRunUsesADifferentKey:
        def test_then_both_runs_perform_the_work(self) -> None:
            first_argument = _unique_argument()
            second_argument = _unique_argument()
            REENTRANT_ARGUMENTS.append(second_argument)

            UniqueJob.perform_async(first_argument)

            assert RUN_LOG == [first_argument, second_argument]

        def test_then_both_runs_are_recorded_as_succeeded(self) -> None:
            REENTRANT_ARGUMENTS.append(_unique_argument())

            UniqueJob.perform_async(_unique_argument())

            job_runs = _job_runs("UniqueJob")
            assert len(job_runs) == 2
            assert all(run.status == JobRunStatus.SUCCEEDED for run in job_runs)

    class TestWhileTheRunIsInFlight:
        def test_then_the_key_is_locked(self) -> None:
            UniqueJob.perform_async(_unique_argument())

            assert LOCK_OBSERVATIONS == [True]

    class TestWhenTheRunSucceeds:
        def test_then_the_lock_is_released(self) -> None:
            argument = _unique_argument()

            UniqueJob.perform_async(argument)

            assert not _lock_exists("UniqueJob", argument)

        def test_then_a_later_run_on_the_same_key_proceeds(self) -> None:
            argument = _unique_argument()

            UniqueJob.perform_async(argument)
            UniqueJob.perform_async(argument)

            assert RUN_LOG == [argument, argument]

    class TestWhenTheRunRaises:
        def test_then_the_lock_is_released(self) -> None:
            argument = _unique_argument()

            with pytest.raises(RuntimeError):
                UniqueFailingJob.perform_async(argument)

            assert not _lock_exists("UniqueFailingJob", argument)

        def test_then_the_job_run_is_recorded_as_failed(self) -> None:
            with pytest.raises(RuntimeError):
                UniqueFailingJob.perform_async(_unique_argument())

            job_runs = _job_runs("UniqueFailingJob")
            assert len(job_runs) == 1
            assert job_runs[0].status == JobRunStatus.FAILED

        def test_then_a_later_run_on_the_same_key_proceeds(self) -> None:
            argument = _unique_argument()

            with pytest.raises(RuntimeError):
                UniqueFailingJob.perform_async(argument)
            with pytest.raises(RuntimeError):
                UniqueFailingJob.perform_async(argument)

            assert RUN_LOG == [argument, argument]


class TestGivenAJobDeclaresNoUniqueKey:
    class TestWhenItRunsTwice:
        def test_then_both_runs_perform_the_work(self) -> None:
            UnkeyedJob.perform_async()
            UnkeyedJob.perform_async()

            assert RUN_LOG == ["unkeyed", "unkeyed"]

        def test_then_both_runs_are_recorded_as_succeeded(self) -> None:
            UnkeyedJob.perform_async()
            UnkeyedJob.perform_async()

            job_runs = _job_runs("UnkeyedJob")
            assert len(job_runs) == 2
            assert all(run.status == JobRunStatus.SUCCEEDED for run in job_runs)


class TestGivenALockHeldByAnotherRun:
    class TestWhenThisRunTriesToReleaseIt:
        def test_then_the_lock_survives_and_the_release_reports_failure(self) -> None:
            key = _lock_key("OwnershipJob", _unique_argument())
            LockService.acquire(key=key, token="owner-token", ttl_seconds=60)

            released = LockService.release(key=key, token="impostor-token")

            assert released is False
            assert bool(CacheClient.get_client().exists(namespaced_key(key)))

            LockService.release(key=key, token="owner-token")

    class TestWhenTheOwnerReleasesIt:
        def test_then_the_lock_is_gone(self) -> None:
            key = _lock_key("OwnershipJob", _unique_argument())
            LockService.acquire(key=key, token="owner-token", ttl_seconds=60)

            released = LockService.release(key=key, token="owner-token")

            assert released is True
            assert not bool(CacheClient.get_client().exists(namespaced_key(key)))


class TestGivenAProcessCouldDieHoldingTheLock:
    class TestWhenTheLockIsTaken:
        def test_then_it_carries_the_jobs_expiry_so_the_key_cannot_be_stranded(self) -> None:
            argument = _unique_argument()

            TtlObservingJob.perform_async(argument)

            assert OBSERVED_TTLS and 0 < OBSERVED_TTLS[0] <= TtlObservingJob.unique_for_seconds
