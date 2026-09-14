from adapters.horizon.j6p import HorizonJ6PAdapter
from adapters.horizon.x5 import HorizonX5Adapter
from adapters.mtk.g720 import MTKG720Adapter


# Platform adapter registry.
# 平台适配器注册表。
ADAPTERS = {
    "x5": HorizonX5Adapter,
    "j6p": HorizonJ6PAdapter,
    "g720": MTKG720Adapter,
}


def get_adapter(platform: str):
    """
    Get platform adapter instance.

    获取指定平台的适配器实例。
    """

    # Normalize platform name.
    # 统一平台名称为小写。
    platform = platform.lower()

    # Check whether the platform is supported.
    # 检查平台是否已经注册。
    if platform not in ADAPTERS:
        raise ValueError(
            f"Unsupported platform: {platform}"
        )

    return ADAPTERS[platform]()