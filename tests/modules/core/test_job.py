from typing import Any, Iterator

import pytest

from modules.account.internal.store.account_repository import AccountRepository
from modules.account.types import Account
from modules.core.celery_app import app as celery_app
from modules.core.common.types import ActorType, AuditActor, JobRunQuery, JobRunStatus
from modules.core.internal.audit.store.audit_log_repository import AuditLogRepository
from modules.core.internal.job_run.store.job_run_repository import JobRunRepository
from modules.core.job import Job


class AccountMutatingJob(Job):
    max_retries = 0

    @classmethod
    def perform(cls, *args: Any, actor: AuditActor, **kwargs: Any) -> str:
        account = Account(
            id="",
            first_name="job",
            last_name="run",
            hashed_password="hashed",
            phone_number=None,
            username="job-run@example.com",
        )
        return AccountRepository.create(account, actor=actor).id


class FailingJob(Job):
    max_retries = 0

    @classmethod
    def perform(cls, *args: Any, actor: AuditActor, **kwargs: Any) -> None:
        raise RuntimeError("job body failed")


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
def clean_collections() -> Iterator[None]:
    JobRunRepository.collection().delete_many({})
    AuditLogRepository.collection().delete_many({})
    AccountRepository.collection().delete_many({})
    yield
    JobRunRepository.collection().delete_many({})
    AuditLogRepository.collection().delete_many({})
    AccountRepository.collection().delete_many({})


def _audit_docs() -> list[dict[str, Any]]:
    return list(AuditLogRepository.collection().find({}))


class TestGivenAJobIsDispatched:
    class TestWhenTheJobSucceeds:
        def test_then_a_job_run_row_transitions_running_to_succeeded(self) -> None:
            AccountMutatingJob.perform_async()

            job_runs = JobRunRepository.query(JobRunQuery(job_name="AccountMutatingJob"), actor=_reader_actor())
            assert len(job_runs) == 1
            job_run = job_runs[0]
            assert job_run.status == JobRunStatus.SUCCEEDED
            assert job_run.started_at is not None
            assert job_run.ended_at is not None

    class TestWhenTheJobMutatesData:
        def test_then_writes_are_attributed_to_the_job_run(self) -> None:
            AccountMutatingJob.perform_async()

            job_run = JobRunRepository.query(JobRunQuery(job_name="AccountMutatingJob"), actor=_reader_actor())[0]
            account_creates = [
                doc
                for doc in _audit_docs()
                if doc["resource_type"] == AccountRepository.collection_name and doc["action"] == "create"
            ]
            assert len(account_creates) == 1
            entry = account_creates[0]
            assert entry["actor_type"] == ActorType.JOB.value
            assert entry["actor_id"] == job_run.id


class TestGivenAJobRaises:
    class TestWhenTheJobBodyFails:
        def test_then_the_job_run_row_is_marked_failed(self) -> None:
            with pytest.raises(RuntimeError):
                FailingJob.perform_async()

            job_runs = JobRunRepository.query(JobRunQuery(job_name="FailingJob"), actor=_reader_actor())
            assert len(job_runs) == 1
            assert job_runs[0].status == JobRunStatus.FAILED
            assert job_runs[0].ended_at is not None


def _reader_actor() -> AuditActor:
    return AuditActor(actor_type=ActorType.WORKER, actor_id="test-reader")
