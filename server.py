from mcp.server import MCPServer
import onnx

mcp = MCPServer("edge-deploy-mcp")


@mcp.tool()
def ping() -> dict[str, str]:
    """Check whether the MCP server is working."""
    return {
        "status": "ok",
        "server": "edge-deploy-mcp",
    }

@mcp.tool()
def inspect_onnx(model_path: str) -> dict:
    """Inspect basic information of an ONNX model."""

    model = onnx.load(model_path)

    return {
        "node_count": len(model.graph.node),
        "inputs": [x.name for x in model.graph.input],
        "outputs": [x.name for x in model.graph.output],
    }

if __name__ == "__main__":
    mcp.run()
