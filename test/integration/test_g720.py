from adapters.registry import get_adapter


# YOLOv5s model root used for G720 integration testing.
# G720 集成测试使用的 YOLOv5s 模型根目录。
MODEL_ROOT = (
    "/data/users/hailong.he/github/mtk_models/"
    "models/perception/object_detection/yolov5s"
)

# INT8 TFLite model used for NCC compilation.
# NCC 编译使用的 INT8 TFLite 模型。
TFLITE_MODEL = f"{MODEL_ROOT}/models/model_int8.tflite"


def test_g720_platform_info():
    """
    Test G720 platform information.

    测试 G720 平台信息获取。
    """
    adapter = get_adapter("g720")

    result = adapter.get_platform_info()

    assert result["vendor"] == "MediaTek"
    assert result["platform"] == "G720"
    assert result["target"] == "mdla"
    assert result["ncc_arch"] == "mdla5.3"

    print("[PASS] G720 platform info")


def test_g720_compile():
    """
    Test G720 model compilation.

    测试 G720 模型编译。
    """
    adapter = get_adapter("g720")

    result = adapter.compile_model(
        model_path=TFLITE_MODEL,
    )

    assert result["status"] == "success"
    assert result["platform"] == "G720"
    assert result["dla_path"].endswith(".dla")

    print(
        f"[PASS] G720 compile: "
        f"{result['dla_path']}"
    )


def test_g720_deploy():
    """
    Test G720 board deployment.

    测试 G720 板端部署。
    """
    adapter = get_adapter("g720")

    result = adapter.deploy_model(
        model_path=MODEL_ROOT,
    )

    assert result["status"] == "success"
    assert result["platform"] == "G720"
    assert result["remote_dir"] == "/root/hailong.he/yolov5s"

    expected_files = {
        "model_int8.dla",
        "input_int8.bin",
        "run_board.sh",
    }

    assert set(result["files"]) == expected_files

    print(
        f"[PASS] G720 deploy: "
        f"{result['remote_dir']}"
    )


def test_g720_verify():
    """
    Test G720 board inference and benchmark.

    测试 G720 板端推理和性能测试。
    """
    adapter = get_adapter("g720")

    result = adapter.verify_model(
        model_path=MODEL_ROOT,
    )

    assert result["status"] == "success"
    assert result["platform"] == "G720"

    # FPS and latency must be successfully parsed.
    # 必须成功解析 FPS 和单次推理耗时。
    assert result["fps"] is not None
    assert result["fps"] > 0

    assert result["latency_ms"] is not None
    assert result["latency_ms"] > 0

    assert result["benchmark_log"].endswith(
        "output/benchmark.log"
    )

    print(
        "[PASS] G720 verify: "
        f"FPS={result['fps']}, "
        f"Latency={result['latency_ms']} ms"
    )


def main():
    """
    Run all G720 integration tests.

    执行全部 G720 集成测试。
    """
    test_g720_platform_info()
    test_g720_compile()
    test_g720_deploy()
    test_g720_verify()

    print("\n[PASS] All G720 integration tests passed.")


if __name__ == "__main__":
    main()