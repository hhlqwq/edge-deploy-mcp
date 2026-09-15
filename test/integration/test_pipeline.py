import asyncio

from mcp import Client
from server import mcp
from pathlib import Path


# G720 INT8 TFLite model used for pipeline integration testing.
# Pipeline 集成测试使用的 G720 INT8 TFLite 模型。
G720_MODEL = (
    "/data/users/hailong.he/github/mtk_models/"
    "models/perception/object_detection/yolov5s/"
    "models/model_int8.tflite"
)


async def test_g720_deploy_pipeline():
    """
    Test the complete G720 deployment pipeline.

    测试 G720 完整模型部署流程。
    """

    async with Client(mcp) as client:
        result = await client.call_tool(
            "deploy_pipeline",
            {
                "platform": "g720",
                "model_path": G720_MODEL,
            },
        )

        # MCP v2 returns tool result as text content.
        # MCP v2 将工具结果返回为文本内容。
        text = result.content[0].text

        assert '"status": "success"' in text
        assert '"platform": "G720"' in text
        # Verify artifact information.
        # 验证编译产物信息。
        assert '"artifact"' in text

        # Verify deployment information.
        # 验证部署信息。
        assert '"deployment"' in text

        # Verify verification information.
        # 验证模型验证信息。
        assert '"verification"' in text

        # Verify runtime benchmark result.
        # 验证运行时性能测试结果。
        assert '"benchmark"' in text
        assert '"latency"' in text
        assert '"throughput"' in text

        # Find generated deployment reports.
        # 查找生成的部署报告。
        report_dir = Path(
            "outputs/reports"
        )

        report_files = list(
            report_dir.glob(
                "g720_*_deployment_report.json"
            )
        )

        # At least one deployment report should exist.
        # 至少应该生成一个部署报告。
        assert report_files

        # Use the latest generated deployment report.
        # 使用最新生成的部署报告。
        report_path = max(
            report_files,
            key=lambda path: path.stat().st_mtime,
        )
        assert report_path.exists()

        # Verify report generation time.
        # 验证报告生成时间。
        report_text = report_path.read_text(
            encoding="utf-8"
        )

        assert '"generated_at"' in report_text
        assert "+08:00" in report_text

        print(
            "[PASS] G720 deploy pipeline"
        )


async def main():
    """
    Run deployment pipeline integration tests.

    执行模型部署 Pipeline 集成测试。
    """

    await test_g720_deploy_pipeline()

    print(
        "\n[PASS] All deployment pipeline "
        "integration tests passed."
    )


if __name__ == "__main__":
    asyncio.run(main())