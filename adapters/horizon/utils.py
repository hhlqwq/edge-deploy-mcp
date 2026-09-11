import re
from pathlib import Path


def parse_horizon_compile_log(
    log_path: str,
) -> dict:
    """
    解析地平线编译日志
    Parse Horizon compile log.
    """

    log_file = Path(log_path)

    if not log_file.exists():
        return {
            "status": "failed",
            "reason": "log file not found",
        }

    text = log_file.read_text(
        errors="ignore"
    )

    result = {}

    # 解析性能信息
    # Parse performance information.
    perf_match = re.search(
        r"FPS=([\d.]+), latency = ([\d.]+) us",
        text,
    )

    if perf_match:
        result["fps"] = float(
            perf_match.group(1)
        )
        result["latency_us"] = float(
            perf_match.group(2)
        )

    # 解析 hbm 路径
    # Parse generated hbm path.
    hbm_match = re.search(
        r"hbm_path:\s*(.*\.hbm)",
        text,
    )

    if hbm_match:
        result["hbm_path"] = (
            hbm_match.group(1).strip()
        )

    return {
        "status": "success",
        **result,
    }


def parse_horizon_compile_output(
    output: str,
) -> dict:
    """
    解析 hb_compile 标准输出
    Parse hb_compile stdout output.
    """

    import re

    result = {}

    perf_match = re.search(
        r"FPS=([\d.]+), latency = ([\d.]+) us",
        output,
    )

    if perf_match:
        result["fps"] = float(
            perf_match.group(1)
        )
        result["latency_us"] = float(
            perf_match.group(2)
        )

    return result