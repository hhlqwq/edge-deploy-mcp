from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Metric:

    value: float
    unit: str


@dataclass
class BenchmarkResult:
    """
    Unified benchmark result.

    统一性能测试结果。
    """

    type: str

    latency: Optional[Metric] = None

    throughput: Optional[Metric] = None

    memory: Optional[Metric] = None

    power: Optional[Metric] = None


    def to_dict(self) -> dict:
        """
        Convert benchmark result to dictionary.

        转换为字典。
        """

        result = {
            "type": self.type,
            "latency": None,
            "throughput": None,
            "memory": None,
            "power": None,
        }

        for key, value in asdict(self).items():

            if value is None:
                continue

            if isinstance(value, dict):
                result[key] = value

        return result