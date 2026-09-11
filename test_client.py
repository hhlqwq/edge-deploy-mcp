import asyncio

from mcp import Client
from server import mcp


async def main():
    async with Client(mcp) as client:
        # Test ping
        result = await client.call_tool(
            "ping",
            {},
        )
        print("=== ping ===")
        print(result.structured_content)

        # Test inspect_onnx
        result = await client.call_tool(
            "inspect_onnx",
            {
                "model_path": "/data/users/hailong.he/github/mtk_models/models/perception/object_detection/yolov5s/models/model_fp32.onnx"
            },
        )

        print("\n=== inspect_onnx ===")
        print("is_error:", result.is_error)
        print("content:", result.content)
        print("structured_content:", result.structured_content)


        result = await client.call_tool(
            "check_model_compatibility",
            {
                "model_path": "/data/users/hailong.he/github/mtk_models/models/perception/object_detection/yolov5s/models/model_fp32.onnx"
            },
        )

        print("\n=== check_model_compatibility ===")
        print(result.content)


        result = await client.call_tool(
            "get_platform_info",
            {
                "platform": "j6p"
            },
        )

        print("\n=== get_platform_info ===")
        print(result.content)


        result = await client.call_tool(
            "compile_model",
            {
                "platform": "j6p",
                "model_path": "/data/users/hailong.he/github/horizon_models/tmp/mcp_test/model_fp32.onnx",
            },
        )

        print("\n=== compile_model ===")
        print(result.content)


        result = await client.call_tool(
            "deploy_model",
            {
                "platform": "j6p",
                "model_path": "/data/users/hailong.he/github/horizon_models/tmp/mcp_test/model_output/model.hbm",
            },
        )

        print("\n=== deploy_model ===")
        print(result.content)

        
if __name__ == "__main__":
    asyncio.run(main())