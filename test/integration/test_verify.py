import asyncio

from mcp import Client
import sys
from pathlib import Path

# 添加项目根目录
# Add project root directory.
ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


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