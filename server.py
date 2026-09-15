from collections import Counter

import onnx
from onnx import TensorProto
from mcp.server import MCPServer
from adapters.registry import get_adapter
from reports.deployment_report import (
    build_deployment_report,
    save_deployment_report,
)


mcp = MCPServer("edge-deploy-mcp")


@mcp.tool()
def ping() -> dict[str, str]:
    """
    检查MCP服务器是否正常工作
    Check whether the MCP server is working.
    """
    return {
        "status": "ok",
        "server": "edge-deploy-mcp",
    }


def get_tensor_info(value_info):
    tensor_type = value_info.type.tensor_type

    shape = []
    for dim in tensor_type.shape.dim:
        if dim.HasField("dim_value"):
            shape.append(dim.dim_value)
        elif dim.HasField("dim_param"):
            shape.append(dim.dim_param)
        else:
            shape.append(None)

    return {
        "name": value_info.name,
        "shape": shape,
        "dtype": TensorProto.DataType.Name(tensor_type.elem_type),
    }


@mcp.tool()
def inspect_onnx(model_path: str) -> dict:
    """
    检查ONNX型号的基本信息
    Inspect basic information of an ONNX model.
    """

    model = onnx.load(model_path)

    operators = Counter(
        node.op_type for node in model.graph.node
    )

    return {
        "ir_version": model.ir_version,
        "opsets": [
            {
                "domain": x.domain or "ai.onnx",
                "version": x.version,
            }
            for x in model.opset_import
        ],
        "node_count": len(model.graph.node),
        "inputs": [
            get_tensor_info(x)
            for x in model.graph.input
        ],
        "outputs": [
            get_tensor_info(x)
            for x in model.graph.output
        ],
        "operators": dict(operators),
    }


@mcp.tool()
def check_model_compatibility(model_path: str) -> dict:
    """
    检查ONNX型号的基本兼容性问题
    Check basic ONNX model compatibility issues.
    """

    model = onnx.load(model_path)

    issues = []

    # 检查动态输入尺寸
    for input_info in model.graph.input:
        for dim in input_info.type.tensor_type.shape.dim:
            if dim.HasField("dim_param") or not dim.HasField("dim_value"):
                issues.append(
                    f"输入 {input_info.name} 包含动态维度"
                )
                break

    # 检查 opset
    opsets = {
        x.domain or "ai.onnx": x.version
        for x in model.opset_import
    }

    return {
        "compatible": len(issues) == 0,
        "opsets": opsets,
        "issues": issues,
    }


@mcp.tool()
def get_platform_info(platform: str) -> dict:
    """
    返回支持的边缘AI平台的信息
    Return information for a supported edge AI platform.
    """

    adapter = get_adapter(platform)
    return adapter.get_platform_info()


@mcp.tool()
def compile_model(
    platform: str,
    model_path: str,
) -> dict:
    """
    为目标边缘AI平台编译模型
    Compile a model for the target edge AI platform.
    """

    adapter = get_adapter(platform)

    return adapter.compile_model(
        model_path=model_path,
    )


@mcp.tool()
def deploy_model(
    platform: str,
    deploy_path: str,
) -> dict:
    """
    将编译产物或部署包部署到目标边缘 AI 板。

    Deploy a compiled artifact or deployment package
    to the target edge AI board.
    """

    adapter = get_adapter(platform)

    return adapter.deploy_model(
        deploy_path,
    )


@mcp.tool()
def verify_model(
    platform: str,
    deploy_path: str,
) -> dict:
    """
    验证目标板上已经部署的模型。

    Verify the deployed model on the target board.
    """

    adapter = get_adapter(platform)

    return adapter.verify_model(
        deploy_path,
    )


@mcp.tool()
def deploy_pipeline(
    platform: str,
    model_path: str,
) -> dict:
    """
    执行模型编译、部署和验证完整流程。

    Run the complete model compile, deploy,
    and verification pipeline.
    """

    # Get target platform adapter.
    # 获取目标平台适配器。
    adapter = get_adapter(platform)

    # Step 1: Compile model.
    # 第一步：编译模型。
    compile_result = adapter.compile_model(
        model_path=model_path,
    )

    if compile_result.get("status") != "success":
        return {
            "status": "failed",
            "platform": platform,
            "stage": "compile",
            "compile": compile_result,
        }

    deploy_path = compile_result.get(
        "deploy_path"
    )

    if not deploy_path:
        return {
            "status": "failed",
            "platform": platform,
            "stage": "compile",
            "reason": (
                "compile_model() did not return deploy_path"
            ),
            "compile": compile_result,
        }

    # Step 2: Deploy compiled artifact or package.
    # 第二步：部署编译产物或部署包。
    deploy_result = adapter.deploy_model(
        deploy_path,
    )

    if deploy_result.get("status") != "success":
        return {
            "status": "failed",
            "platform": platform,
            "stage": "deploy",
            "compile": compile_result,
            "deploy": deploy_result,
        }

    # Step 3: Verify deployed model on target board.
    # 第三步：在目标板验证部署后的模型。
    verify_result = adapter.verify_model(
        deploy_path,
    )

    if verify_result.get("status") != "success":
        return {
            "status": "failed",
            "platform": platform,
            "stage": "verify",
            "compile": compile_result,
            "deploy": deploy_result,
            "verify": verify_result,
        }
    
    # Build normalized deployment report.
    # 构建统一部署报告。
    report = build_deployment_report(
        pipeline_result={
            "status": "success",
            "platform": compile_result.get(
                "platform",
                platform,
            ),
            "model_path": model_path,
            "artifact": {
                "path": compile_result.get(
                    "artifact_path"
                ),
            },
            "deployment": {
                "status": deploy_result.get(
                    "status"
                ),
                "remote_path": (
                    deploy_result.get("remote_path")
                    or deploy_result.get("remote_dir")
                ),
            },
            "verification": {
                "type": verify_result.get(
                    "verification_type"
                ),
                "benchmark": verify_result.get(
                    "benchmark"
                ),
            },
        }
    )

    # Use report generation time in the file name.
    # 使用报告生成时间生成唯一文件名。
    report_time = (
        report["generated_at"]
        .replace(":", "")
        .replace("-", "")
    )

    report_path = save_deployment_report(
        report=report,
        output_path=(
            "outputs/reports/"
            f"{platform}_{report_time}_deployment_report.json"
        ),
    )

    return {
        "status": "success",

        # Platform name.
        # 平台名称。
        "platform": compile_result.get(
            "platform",
            platform,
        ),

        # Original model.
        # 原始模型路径。
        "model_path": model_path,

        # Compiled artifact information.
        # 编译产物信息。
        "artifact": {
            "path": compile_result.get(
                "artifact_path"
            ),
        },

        # Deployment information.
        # 部署信息。
        "deployment": {
            "status": deploy_result.get(
                "status"
            ),
            "remote_path": (
                deploy_result.get("remote_path")
                or deploy_result.get("remote_dir")
            ),
        },

        # Verification information.
        # 验证信息。
        "verification": {

            # Verification type.
            # 验证类型。
            "type": verify_result.get(
                "verification_type"
            ),

            # Benchmark result.
            # 性能测试结果。
            "benchmark": verify_result.get(
                "benchmark"
            ),
        },

        # Detailed platform-specific results.
        # 保留平台详细信息。
        "details": {
            "compile": compile_result,
            "deploy": deploy_result,
            "verify": verify_result,
        },

        # Deployment report information.
        # 部署报告信息。
        "report": {
            "path": report_path,
            "content": report,
        },
    }


if __name__ == "__main__":
    mcp.run()