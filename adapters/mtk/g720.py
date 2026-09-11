import os
import re
from pathlib import Path
import subprocess

from adapters.base import BasePlatformAdapter
from config.loader import get_platform_config


class MTKG720Adapter(BasePlatformAdapter):
    """
    MTK G720 platform adapter.

    MTK G720 平台适配器。
    """

    # Load platform configuration.
    # 加载平台配置。
    PLATFORM_CONFIG = get_platform_config(
        "mtk",
        "g720",
    )

    # MTK docker container.
    # MTK 工具链容器。
    CONTAINER_NAME = PLATFORM_CONFIG["container"]

    # Target accelerator.
    # 目标加速器。
    TARGET = PLATFORM_CONFIG["target"]

    # NCC compiler architecture.
    # NCC 编译架构。
    NCC_ARCH = PLATFORM_CONFIG["ncc_arch"]

    # NCC compiler path.
    # NCC 编译器路径。
    COMPILER = PLATFORM_CONFIG["compiler"]

    # Docker mounted root directory.
    # Docker 挂载根目录。
    MOUNT_ROOT = Path(
        PLATFORM_CONFIG["mount_root"]
    )

    # Board SSH host.
    # 开发板 SSH 地址。
    SSH_HOST = PLATFORM_CONFIG["ssh_host"]

    # Board deployment directory.
    # 板端部署目录。
    REMOTE_DIR = PLATFORM_CONFIG["remote_dir"]

    # NCC compiler runtime library path.
    # NCC 编译器运行时依赖动态库路径，用于设置 LD_LIBRARY_PATH。
    NCC_LIB = PLATFORM_CONFIG["ncc_lib"]

    def get_platform_info(self) -> dict:
        """
        Get platform information.

        获取平台信息。
        """

        return {
            "vendor": "MediaTek",
            "platform": "G720",
            "container": self.CONTAINER_NAME,
            "target": self.TARGET,
            "ncc_arch": self.NCC_ARCH,
        }


    def compile_model(
        self,
        model_path: str,
    ) -> dict:
        """
        Compile TFLite model to DLA.

        将 TFLite 模型编译为 DLA。
        """

        model = Path(model_path)

        if not model.exists():
            return {
                "status": "failed",
                "reason": f"Model not found: {model}",
            }

        if model.suffix != ".tflite":
            return {
                "status": "failed",
                "reason": "G720 compiler requires .tflite model",
            }

        output_path = model.with_suffix(".dla")

        cmd = (
            f"{self.COMPILER} "
            f"--arch={self.NCC_ARCH} "
            "--suppress-output "
            "--disallow-bridge "
            f"{model} "
            f"-d {output_path}"
        )

        # Prepare compiler environment.
        # 准备编译环境变量。
        env = os.environ.copy()

        # Add NCC runtime libraries required by ncc-tflite.
        # 添加 ncc-tflite 编译所需动态库路径。
        env["LD_LIBRARY_PATH"] = (
            f"{self.NCC_LIB}:"
            f"{env.get('LD_LIBRARY_PATH', '')}"
        )


        result = subprocess.run(
            [
                "docker",
                "exec",
                self.CONTAINER_NAME,
                "bash",
                "-lc",
                cmd,
            ],
            capture_output=True,
            text=True,
            env=env,
        )

        if result.returncode != 0:
            return {
                "status": "failed",
                "stderr": result.stderr,
            }

        return {
            "status": "success",
            "platform": "G720",
            "tflite_path": str(model),
            "dla_path": str(output_path),
        }


    def deploy_model(
        self,
        model_root: str,
    ) -> dict:
        """
        Deploy G720 inference package to board.

        部署 G720 推理工程到开发板。
        """

        root = Path(model_root)

        dla_file = (
            root
            / "models"
            / "model_int8.dla"
        )

        input_file = (
            root
            / "examples"
            / "input"
            / "input_int8.bin"
        )

        run_script = (
            root
            / "deploy"
            / "inference_demo"
            / "run_board.sh"
        )

        # Check required deployment files.
        # 检查部署所需文件。
        for file in [
            dla_file,
            input_file,
            run_script,
        ]:
            if not file.exists():
                return {
                    "status": "failed",
                    "reason": (
                        f"Missing file: {file}"
                    ),
                }


        remote_dir = (
            f"{self.REMOTE_DIR}/"
            f"{root.name}"
        )

        commands = [
            (
                "mkdir",
                [
                    "ssh",
                    self.SSH_HOST,
                    f"mkdir -p {remote_dir}",
                ],
            ),
            (
                "dla",
                [
                    "scp",
                    str(dla_file),
                    f"{self.SSH_HOST}:{remote_dir}/model_int8.dla",
                ],
            ),
            (
                "input",
                [
                    "scp",
                    str(input_file),
                    f"{self.SSH_HOST}:{remote_dir}/input_int8.bin",
                ],
            ),
            (
                "script",
                [
                    "scp",
                    str(run_script),
                    f"{self.SSH_HOST}:{remote_dir}/run_board.sh",
                ],
            ),
        ]


        for name, cmd in commands:

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                return {
                    "status": "failed",
                    "step": name,
                    "stderr": result.stderr,
                }


        return {
            "status": "success",
            "platform": "G720",
            "remote_dir": remote_dir,
            "files": [
                "model_int8.dla",
                "input_int8.bin",
                "run_board.sh",
            ],
        }


    def verify_model(
        self,
        model_root: str,
    ) -> dict:
        """
        Run G720 board inference verification.

        执行 G720 板端推理验证。
        """

        root = Path(model_root)

        remote_dir = (
            f"{self.REMOTE_DIR}/"
            f"{root.name}"
        )

        remote_script = (
            f"{remote_dir}/run_board.sh"
        )

        # Check board script and execute inference.
        # 检查板端脚本并执行推理。
        cmd = (
            f"chmod +x {remote_script} && "
            f"{remote_script}"
        )

        result = subprocess.run(
            [
                "ssh",
                self.SSH_HOST,
                cmd,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return {
                "status": "failed",
                "platform": "G720",
                "stderr": result.stderr,
                "stdout": result.stdout,
            }

                # Collect benchmark result.
        # 获取性能测试结果。
        benchmark_log = (
            f"{remote_dir}/output/benchmark.log"
        )

        parse_cmd = (
            f"cat {benchmark_log}"
        )

        log_result = subprocess.run(
            [
                "ssh",
                self.SSH_HOST,
                parse_cmd,
            ],
            capture_output=True,
            text=True,
        )


        benchmark_text = log_result.stdout


        fps = None
        latency_ms = None


        # Parse average FPS.
        # 解析平均 FPS。
        fps_match = re.search(
            r"Avg\. FPS\s*:\s*([\d.]+)",
            benchmark_text,
        )

        if fps_match:
            fps = float(
                fps_match.group(1)
            )

        # Parse latency.
        # 解析单次推理耗时。
        latency_match = re.search(
            r"\(([\d.]+)\s*ms/inf\)",
            benchmark_text,
        )

        if latency_match:
            latency_ms = float(
                latency_match.group(1)
            )


        return {
            "status": "success",
            "platform": "G720",
            "remote_dir": remote_dir,
            "fps": fps,
            "latency_ms": latency_ms,
            "benchmark_log": benchmark_log,
        }