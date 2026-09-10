from adapters.horizon.x5 import HorizonX5Adapter


ADAPTERS = {
    "x5": HorizonX5Adapter,
}


def get_adapter(platform: str):
    platform = platform.lower()

    if platform not in ADAPTERS:
        raise ValueError(f"Unsupported platform: {platform}")

    return ADAPTERS[platform]()