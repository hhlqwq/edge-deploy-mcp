from pathlib import Path

import yaml


# 加载平台配置
# Load platform configuration.
def load_platform_config() -> dict:
    config_path = (
        Path(__file__).parent / "platforms.yaml"
    )

    with open(
        config_path,
        "r",
        encoding="utf-8",
    ) as f:
        return yaml.safe_load(f)


# 获取指定平台配置
# Get configuration for specified platform.
def get_platform_config(
    vendor: str,
    platform: str,
) -> dict:

    config = load_platform_config()

    return config[vendor][platform]