import asyncio

from mcp import Client
from server import mcp


async def main():
    async with Client(mcp) as client:
        # 验证 J6P 板端已部署模型
        # Verify the deployed model on the J6P board.
        result = await client.call_tool(
            "verify_model",
            {
                "platform": "j6p",
                "model_path": "/data/users/hailong.he/github/horizon_models/tmp/mcp_test/model_output/model.hbm",
            },
        )

        print(result.content)


if __name__ == "__main__":
    asyncio.run(main())