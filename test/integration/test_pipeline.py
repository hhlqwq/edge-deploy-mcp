import asyncio

from mcp import Client

from server import mcp


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
        assert '"artifact_path"' in text
        assert '"deploy_path"' in text
        assert '"fps"' in text
        assert '"latency_ms"' in text

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