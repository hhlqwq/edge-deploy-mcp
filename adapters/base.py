from abc import ABC, abstractmethod


class BasePlatformAdapter(ABC):
    """
    Base interface for edge AI platform adapters.
    """

    @abstractmethod
    def get_platform_info(self) -> dict:
        """
        Return platform information.
        """
        pass

    @abstractmethod
    def compile_model(
        self,
        model_path: str,
    ) -> dict:
        """
        Compile model for target platform.
        """
        pass