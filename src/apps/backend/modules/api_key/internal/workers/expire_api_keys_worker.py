from typing import Any

from modules.api_key.api_key_service import ApiKeyService
from modules.application.common.types import ActorType, AuditActor
from modules.application.worker import Worker
from modules.logger.logger import Logger

# The worker acts on behalf of the system, not a signed-in account, so every expiry it records is
# attributed to this worker actor in the audit trail.
EXPIRE_API_KEYS_WORKER_ACTOR = AuditActor(actor_type=ActorType.WORKER, actor_id="expire_api_keys_worker")


class ExpireApiKeysWorker(Worker):
    queue = "default"
    max_retries = 1
    cron_schedule = "0 0 * * *"

    @classmethod
    def perform(cls, *args: Any, **kwargs: Any) -> None:
        try:
            expired_keys = ApiKeyService.expire_expired_keys(actor=EXPIRE_API_KEYS_WORKER_ACTOR)
            for key in expired_keys:
                Logger.info(message=f"ExpireApiKeysWorker: expired API key id={key.id} name={key.name}")
        except Exception as exc:
            Logger.error(message=f"ExpireApiKeysWorker failed: {exc}")
