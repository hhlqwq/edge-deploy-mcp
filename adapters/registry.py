from adapters.horizon.x5 import HorizonX5Adapter
from adapters.horizon.j6p import HorizonJ6PAdapter


ADAPTERS = {
    "x5": HorizonX5Adapter,
    "j6p": HorizonJ6PAdapter,
}


def get_adapter(platform: str):
    platform = platform.lower()

    if platform not in ADAPTERS:
        raise ValueError(f"Unsupported platform: {platform}")

    return ADAPTERS[platform]()