from abc import ABC, abstractmethod


class BasePlatformAdapter(ABC):
    """
    边缘 AI 平台适配器基础接口。
    Base interface for edge AI platform adapters.
    """

    @abstractmethod
    def get_platform_info(self) -> dict:
        """
        返回平台基础信息。

        Return basic platform information.
        """
        pass

    @abstractmethod
    def compile_model(
        self,
        model_path: str,
    ) -> dict:
        """
        编译源模型并生成目标平台可执行模型。

        Compile the source model into a target-platform artifact.

        返回结果应至少包含：
        The result should contain at least:

        - status
        - platform
        - artifact_path
        - deploy_path

        artifact_path:
            编译生成的核心模型文件，例如 HBM 或 DLA。
            Primary compiled artifact, such as HBM or DLA.

        deploy_path:
            后续传给 deploy_model() 的路径。
            可以是单个模型文件，也可以是完整部署包目录。

            Path passed to deploy_model().
            It may be a model artifact or a deployment package directory.
        """
        pass

    @abstractmethod
    def deploy_model(
        self,
        deploy_path: str,
    ) -> dict:
        """
        将编译产物或部署包部署到目标板。

        Deploy the compiled artifact or deployment package
        to the target board.
        """
        pass

    @abstractmethod
    def verify_model(
        self,
        deploy_path: str,
    ) -> dict:
        """
        在目标板上验证已部署模型，并返回验证结果。

        Verify the deployed model on the target board
        and return verification results.
        """
        pass