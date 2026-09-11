import subprocess
from pathlib import Path

from adapters.base import BasePlatformAdapter

class HorizonJ6PAdapter(BasePlatformAdapter):

    CONTAINER_NAME = "hhl_j6_391"
    MARCH = "nash-p"

    # 当前 J6 Docker 挂载的宿主机目录
    MOUNT_ROOT = Path(
        "/data/users/hailong.he/github/horizon_models"
    )

    def get_platform_info(self) -> dict:
        return {
            "vendor": "Horizon",
            "platform": "J6P",
            "container": self.CONTAINER_NAME,
            "march": self.MARCH,
        }

    def compile_model(
        self,
        model_path: str,
    ) -> dict:

        model = Path(model_path).resolve()

        if not model.exists():
            raise FileNotFoundError(
                f"模型不存在: {model}"
            )

        if model.suffix.lower() != ".onnx":
            raise ValueError(
                f"当前只支持 ONNX 模型: {model}"
            )

        # 防止传入 Docker 无法访问的路径
        if not model.is_relative_to(self.MOUNT_ROOT):
            raise ValueError(
                f"模型必须位于 J6 Docker 挂载目录下: "
                f"{self.MOUNT_ROOT}"
            )

        workdir = model.parent

        # 1. 自动生成编译配置
        config_result = subprocess.run(
            [
                "docker",
                "exec",
                "-w",
                str(workdir),
                self.CONTAINER_NAME,
                "hb_config_generator",
                "-s",
                "-m",
                model.name,
                "--march",
                self.MARCH,
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if config_result.returncode != 0:
            return {
                "status": "failed",
                "stage": "config",
                "stderr": config_result.stderr,
            }

        config_path = workdir / "simple_compile_config.yaml"

        # 2. 编译模型
        compile_result = subprocess.run(
            [
                "docker",
                "exec",
                "-w",
                str(workdir),
                self.CONTAINER_NAME,
                "hb_compile",
                "-c",
                config_path.name,
            ],
            capture_output=True,
            text=True,
            timeout=1800,
        )

        hbm_path = workdir / "model_output" / "model.hbm"

        if compile_result.returncode != 0:
            return {
                "status": "failed",
                "stage": "compile",
                "stderr": compile_result.stderr,
            }

        return {
            "status": "success",
            "platform": "J6P",
            "model_path": str(model),
            "config_path": str(config_path),
            "hbm_path": str(hbm_path),
        }

    def deploy_model(
        self,
        model_path: str,
    ) -> dict:

        model = Path(model_path).resolve()

        if not model.exists():
            raise FileNotFoundError(
                f"模型不存在: {model}"
            )

        if model.suffix.lower() != ".hbm":
            raise ValueError(
                f"J6P 部署模型必须是 .hbm: {model}"
            )

        remote_dir = "/root/hehailong/mcp_test"
        remote_path = f"{remote_dir}/{model.name}"

        result = subprocess.run(
            [
                "scp",
                str(model),
                f"j6p:{remote_path}",
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            return {
                "status": "failed",
                "stage": "deploy",
                "stderr": result.stderr,
            }

        return {
            "status": "success",
            "platform": "J6P",
            "local_path": str(model),
            "remote_path": remote_path,
        }
    

    def verify_model(
        self,
        model_path: str,
    ) -> dict:
        """
        验证部署到目标板的模型
        Verify deployed model on target board.
        """

        model = Path(model_path).resolve()

        if model.suffix.lower() != ".hbm":
            raise ValueError(
                f"J6P 验证模型必须是 .hbm: {model}"
            )

        remote_path = (
            f"/root/hehailong/mcp_test/{model.name}"
        )

        result = subprocess.run(
            [
                "ssh",
                "j6p",
                f"ls -lh {remote_path}",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return {
                "status": "failed",
                "stage": "verify",
                "stderr": result.stderr,
            }

        return {
            "status": "success",
            "platform": "J6P",
            "remote_path": remote_path,
            "info": result.stdout.strip(),
        }