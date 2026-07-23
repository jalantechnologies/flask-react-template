from datetime import UTC, datetime

from modules.core.common.types import REDACTED, ActorType, AuditActor, JobArguments, JobRun, JobRunStatus
from modules.core.internal.audit.audit_writer import SENSITIVE_FIELD_KEYWORDS
from modules.core.internal.job_run.store.job_run_repository import JobRunRepository

JOB_RUNNER_BOOTSTRAP_ACTOR = AuditActor(actor_type=ActorType.WORKER, actor_id="job_runner")


class JobRunService:
    @staticmethod
    def start(*, job_name: str, arguments: JobArguments, retry_count: int) -> JobRun:
        entity = JobRun(
            id="",
            job_name=job_name,
            status=JobRunStatus.RUNNING,
            arguments=JobRunService._redact(arguments),
            retry_count=retry_count,
            started_at=datetime.now(UTC),
        )
        return JobRunRepository.create(entity, actor=JOB_RUNNER_BOOTSTRAP_ACTOR)

    @staticmethod
    def mark_succeeded(*, job_run_id: str) -> None:
        JobRunService._finalize(job_run_id=job_run_id, status=JobRunStatus.SUCCEEDED)

    @staticmethod
    def mark_failed(*, job_run_id: str) -> None:
        JobRunService._finalize(job_run_id=job_run_id, status=JobRunStatus.FAILED)

    @staticmethod
    def _finalize(*, job_run_id: str, status: JobRunStatus) -> None:
        JobRunRepository.update(
            job_run_id,
            {"status": status.value, "ended_at": datetime.now(UTC)},
            actor=AuditActor(actor_type=ActorType.JOB, actor_id=job_run_id),
        )

    @staticmethod
    def _redact(arguments: JobArguments) -> JobArguments:
        return {name: (REDACTED if JobRunService._is_sensitive(name) else value) for name, value in arguments.items()}

    @staticmethod
    def _is_sensitive(name: str) -> bool:
        lowered = name.lower()
        return any(keyword in lowered for keyword in SENSITIVE_FIELD_KEYWORDS)
