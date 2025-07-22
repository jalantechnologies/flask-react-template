from abc import ABC, abstractmethod
from typing import Dict, Optional
from modules.logger.logger import Logger


class BaseAccountDeletionHook(ABC):
    """Base class for account deletion hooks"""

    @property
    @abstractmethod
    def hook_name(self) -> str:
        """Unique name for this hook"""
        pass

    @abstractmethod
    def execute(self, account_id: str) -> None:
        """Execute the cleanup logic for this module"""
        pass


class AccountDeletionRegistry:

    _hooks: Dict[str, BaseAccountDeletionHook] = {}

    @classmethod
    def register_hook(cls, hook: BaseAccountDeletionHook) -> None:
        if hook.hook_name in cls._hooks:
            Logger.warn(message=f"Account deletion hook '{hook.hook_name}' is already registered. Overwriting.")

        cls._hooks[hook.hook_name] = hook
        Logger.info(message=f"Registered account deletion hook: {hook.hook_name}")

    @classmethod
    def unregister_hook(cls, hook_name: str) -> None:
        if hook_name in cls._hooks:
            del cls._hooks[hook_name]
            Logger.info(message=f"Unregistered account deletion hook: {hook_name}")

    @classmethod
    def get_hook(cls, hook_name: str) -> Optional[BaseAccountDeletionHook]:
        return cls._hooks.get(hook_name)

    @classmethod
    def get_all_hooks(cls) -> Dict[str, BaseAccountDeletionHook]:
        return cls._hooks.copy()

    @classmethod
    def execute_all_hooks(cls, account_id: str) -> Dict[str, bool]:
        results = {}

        Logger.info(message=f"Executing {len(cls._hooks)} account deletion hooks for account {account_id}")

        for hook_name, hook in cls._hooks.items():
            try:
                Logger.info(message=f"Executing account deletion hook: {hook_name}")
                hook.execute(account_id)
                results[hook_name] = True
                Logger.info(message=f"Successfully executed account deletion hook: {hook_name}")

            except Exception as e:
                Logger.error(message=f"Failed to execute account deletion hook '{hook_name}': {str(e)}")
                results[hook_name] = False

        successful_hooks = sum(1 for success in results.values() if success)
        Logger.info(message=f"Account deletion hooks completed: {successful_hooks}/{len(results)} successful")

        return results
