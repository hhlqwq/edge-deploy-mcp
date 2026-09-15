import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo


def build_deployment_report(
    pipeline_result: dict,
) -> dict:
    """
    Build a normalized deployment report from pipeline result.

    根据部署 Pipeline 结果构建统一部署报告。
    """

    # Build normalized report structure.
    # 构建统一的报告结构。
    return {
        # Report generation time in China Standard Time.
        # 报告生成时间，使用北京时间。
        "generated_at": datetime.now(
            ZoneInfo("Asia/Shanghai")
        ).isoformat(),

        # Pipeline execution status.
        # Pipeline 执行状态。
        "status": pipeline_result.get(
            "status"
        ),

        # Target platform.
        # 目标平台。
        "platform": pipeline_result.get(
            "platform"
        ),

        # Model information.
        # 模型信息。
        "model": {
            "path": pipeline_result.get(
                "model_path"
            ),
            "artifact": pipeline_result.get(
                "artifact"
            ),
        },

        # Deployment information.
        # 部署信息。
        "deployment": pipeline_result.get(
            "deployment"
        ),

        # Verification and benchmark information.
        # 验证与性能测试信息。
        "verification": pipeline_result.get(
            "verification"
        ),
    }


def save_deployment_report(
    report: dict,
    output_path: str,
) -> str:
    """
    Save deployment report as JSON file.

    将部署报告保存为 JSON 文件。
    """

    path = Path(output_path)

    # Ensure parent directory exists.
    # 确保输出目录存在。
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Write report as formatted JSON.
    # 将报告写入格式化 JSON 文件。
    path.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return str(path)