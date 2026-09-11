from abc import ABC, abstractmethod


class BasePlatformAdapter(ABC):
    """
    边缘AI平台适配器的基本接口
    Base interface for edge AI platform adapters.
    """

    @abstractmethod
    def get_platform_info(self) -> dict:
        """
        返回平台信息
        Return platform information.
        """
        pass

    @abstractmethod
    def compile_model(
        self,
        model_path: str,
    ) -> dict:
        """
        为目标平台编译模型
        Compile model for target platform.
        """
        pass

    @abstractmethod
    def deploy_model(
        self,
        model_path: str,
    ) -> dict:
        """
        将编译后的模型部署到目标板
        Deploy compiled model to target board.
        """
        pass

    @abstractmethod
    def verify_model(
        self,
        model_path: str,
    ) -> dict:
        """
        验证目标板上部署的模型
        Verify deployed model on target board.
        """
        pass