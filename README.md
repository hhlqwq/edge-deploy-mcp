# Edge Deploy MCP

Edge Deploy MCP 是一个面向边缘 AI 芯片平台的模型部署 MCP Server，用于统一不同芯片厂商的模型编译、板端部署、验证和性能测试流程。

Edge Deploy MCP is an MCP server for edge AI deployment. It provides unified tools for model compilation, board deployment, verification, and benchmarking across multiple edge AI platforms.

---

## Project Status / 项目状态

| Platform | Compile | Deploy | Verify | Benchmark | Status |
| --- | --- | --- | --- | --- | --- |
| Horizon J6P | ONNX → HBM | HBM → Board | 板端产物检查 | 编译阶段 FPS / Latency | ✅ Verified |
| MediaTek G720 | INT8 TFLite → DLA | 部署包 → Board | NeuronRT 真实推理 | 板端 FPS / Latency | ✅ Verified |
| Horizon X5 | Adapter Skeleton | TBD | TBD | TBD | 🚧 In Progress |

> `Verified` 仅表示已经在真实工具链和目标开发板上完成验证。未验证能力不会标记为 Verified。

---

## Goals / 项目目标

不同边缘 AI 芯片通常具有完全不同的部署流程，例如：

- Horizon：`hb_config_generator`、`hb_compile`、HBM Runtime
- MediaTek：NeuroPilot、NCC、NeuronRT
- 不同平台的输入模型格式、量化方式、编译参数、部署目录、Runtime 和 Benchmark 方式均可能不同

本项目通过 Adapter 层屏蔽平台差异，对外暴露统一 MCP Tool，使上层 AI Agent 不需要了解每个芯片的具体工具链命令。

---

## Architecture / 项目架构

```text
                         AI Agent
                            │
                            ▼
                     Edge Deploy MCP
                            │
        ┌───────────────────┼────────────────────┐
        │                   │                    │
        ▼                   ▼                    ▼
  inspect_onnx        compile_model        deploy_pipeline
        │                   │                    │
        │                   ▼                    ▼
        │            Adapter Registry      compile_model
        │                   │                    │
        │          ┌────────┴────────┐           ▼
        │          │                 │      deploy_model
        │          ▼                 ▼           │
        │     Horizon J6P       MTK G720         ▼
        │          │                 │      verify_model
        │          ▼                 ▼
        │      hb_compile        ncc-tflite
        │          │                 │
        │          ▼                 ▼
        │         HBM               DLA
        │          │                 │
        └──────────┴─────────────────┘
                            │
                            ▼
                       Target Board
```

---

## Unified Deployment Flow / 统一部署流程

统一接口：

```text
compile_model(model_path)
        │
        ▼
 artifact_path
 deploy_path
        │
        ▼
deploy_model(deploy_path)
        │
        ▼
verify_model(deploy_path)
```

### `model_path`

源模型路径。

示例：

```text
J6P  → model.onnx
G720 → model_int8.tflite
```

### `artifact_path`

平台工具链编译生成的核心模型产物。

示例：

```text
J6P  → model.hbm
G720 → model_int8.dla
```

### `deploy_path`

部署阶段使用的路径，可以是单个编译模型文件，也可以是完整部署目录。

J6P：

```text
model.onnx
    ↓
model.hbm

artifact_path = model.hbm
deploy_path   = model.hbm
```

G720：

```text
model_int8.tflite
        ↓
model_int8.dla

artifact_path = models/model_int8.dla
deploy_path   = yolov5s/
```

---

## MCP Tools / MCP 工具

### `ping`

MCP Server 基础连通性测试。

### `inspect_onnx`

解析 ONNX 模型结构，包括：

- IR Version
- Opset Version
- Node Count
- Inputs
- Outputs
- Tensor Shape
- Tensor Data Type
- Operator Statistics

### `check_model_compatibility`

执行基础模型兼容性检查，目前主要包括：

- ONNX 模型可读性
- 输入动态维度检查
- Opset 信息
- 基础模型结构检查

### `get_platform_info`

获取平台注册信息。

```text
get_platform_info(platform)
```

G720 返回示例：

```json
{
  "vendor": "MediaTek",
  "platform": "G720",
  "container": "...",
  "target": "mdla",
  "ncc_arch": "mdla5.3"
}
```

### `compile_model`

调用目标平台 Adapter 编译模型。

```text
compile_model(
    platform,
    model_path
)
```

统一字段：

```json
{
  "status": "success",
  "platform": "...",
  "model_path": "...",
  "artifact_path": "...",
  "deploy_path": "..."
}
```

### `deploy_model`

将编译产物或部署包部署到目标开发板。

```text
deploy_model(
    platform,
    deploy_path
)
```

### `verify_model`

验证已经部署到目标板上的模型。

```text
verify_model(
    platform,
    deploy_path
)
```

当前：

- J6P：验证 HBM 已成功部署到板端
- G720：执行真实 NeuronRT 推理和 Benchmark

### `deploy_pipeline`

执行完整部署链路：

```text
deploy_pipeline(
    platform,
    model_path
)
```

内部自动执行：

```text
get_adapter()
      ↓
compile_model()
      ↓
deploy_path
      ↓
deploy_model()
      ↓
verify_model()
```

返回结构：

```json
{
  "status": "success",
  "platform": "...",
  "model_path": "...",
  "artifact_path": "...",
  "deploy_path": "...",
  "compile": {},
  "deploy": {},
  "verify": {}
}
```

同一个 `deploy_pipeline` 已在 J6P 和 G720 上完成真实验证。

---

## Horizon J6P

当前流程：

```text
ONNX
 │
 ▼
hb_config_generator
 │
 ▼
hb_compile
 │
 ▼
HBM
 │
 ▼
SCP
 │
 ▼
J6P Board
```

### Compile

使用：

```text
hb_config_generator
hb_compile
```

目标 March：

```text
nash-p
```

编译结果示例：

```json
{
  "status": "success",
  "platform": "J6P",
  "model_path": ".../model_fp32.onnx",
  "artifact_path": ".../model_output/model.hbm",
  "deploy_path": ".../model_output/model.hbm",
  "hbm_path": ".../model_output/model.hbm",
  "fps": 1335.63,
  "latency_us": 748.7
}
```

### Deploy

```text
model.hbm
   ↓ SCP
J6P Board
```

### Verify

当前 `verify_model()` 验证板端 HBM 文件是否成功部署。

> 当前 J6P 的 FPS / Latency 来自 Horizon 编译阶段性能输出，不是 MCP 当前实现中的真实板端 Runtime Benchmark。

后续将增加真实输入推理、Runtime Benchmark 和精度验证。

---

## MediaTek G720

当前使用 MediaTek NeuroPilot 工具链。

完整流程：

```text
INT8 TFLite
     │
     ▼
 ncc-tflite
     │
     ▼
    DLA
     │
     ▼
Deployment Package
     │
     ▼
 G720 Board
     │
     ▼
  NeuronRT
     │
     ▼
Benchmark
```

### Compiler

当前编译器：

```text
ncc-tflite
```

目标架构：

```text
mdla5.3
```

核心参数：

```text
--arch=mdla5.3
--suppress-output
--disallow-bridge
```

其中：

- `--arch=mdla5.3`：目标 NPU 架构为 MDLA 5.3
- `--suppress-output`：保留原生 MDLA 输出，避免不需要的输出转换路径
- `--disallow-bridge`：禁止 NCC 自动插入其它硬件目标的数据转换 Bridge

### Deployment Package

G720 部署的是完整推理包，而不是单个 DLA：

```text
model_package/
├── models/
│   └── model_int8.dla
├── examples/
│   └── input/
│       └── input_int8.bin
└── deploy/
    └── inference_demo/
        └── run_board.sh
```

所以：

```text
artifact_path = models/model_int8.dla
deploy_path   = model_package/
```

### Board Inference

板端使用 NeuronRT。

验证流程：

```text
Real Input Smoke Test
        ↓
Warmup × 10
        ↓
Benchmark × 100
        ↓
FPS / Latency
```

运行脚本生成：

```text
output/
├── benchmark.log
├── benchmark_resource.txt
├── neuronrt_version.txt
├── system.txt
├── SHA256SUMS
├── benchmark_0.bin
├── benchmark_1.bin
└── benchmark_2.bin
```

MCP 从真实 `benchmark.log` 中解析：

```text
Avg. FPS
ms/inf
```

实际返回示例：

```json
{
  "status": "success",
  "platform": "G720",
  "remote_dir": "...",
  "fps": 98.58,
  "latency_ms": 10.0265,
  "benchmark_log": ".../output/benchmark.log"
}
```

---

## Adapter Design / Adapter 设计

所有平台 Adapter 继承：

```python
BasePlatformAdapter
```

统一接口：

```python
get_platform_info()

compile_model(
    model_path: str,
)

deploy_model(
    deploy_path: str,
)

verify_model(
    deploy_path: str,
)
```

平台注册由：

```text
adapters/registry.py
```

统一管理。

示例：

```python
get_adapter("j6p")
get_adapter("g720")
get_adapter("x5")
```

---

## Configuration / 平台配置

平台环境配置统一放在：

```text
config/platforms.yaml
```

主要用于配置：

```text
Docker container
Compiler path
Compiler architecture
Docker mount root
SSH alias
Remote deployment directory
Runtime library path
```

示例结构：

```yaml
horizon:
  j6p:
    container: <container_name>
    ssh_host: <ssh_alias>
    march: nash-p
    mount_root: <mounted_project_root>
    remote_dir: <remote_directory>

mtk:
  g720:
    container: <container_name>
    ssh_host: <ssh_alias>
    target: mdla
    ncc_arch: mdla5.3
    mount_root: <mounted_project_root>
    compiler: <ncc_tflite_path>
    ncc_lib: <ncc_library_path>
    remote_dir: <remote_directory>
```

---

## SSH Configuration / SSH 配置

为了避免在仓库中保存开发板 IP 和登录信息，推荐通过：

```text
~/.ssh/config
```

配置 SSH Alias。

示例：

```text
Host j6p
    HostName <board_ip>
    User <user>

Host g720
    HostName <board_ip>
    User <user>
```

项目配置只保存：

```yaml
ssh_host: j6p
```

或：

```yaml
ssh_host: g720
```

---

## Project Structure / 项目结构

```text
edge-deploy-mcp/
├── adapters/
│   ├── base.py
│   ├── registry.py
│   ├── horizon/
│   │   ├── j6p.py
│   │   ├── x5.py
│   │   └── utils.py
│   └── mtk/
│       ├── __init__.py
│       └── g720.py
├── config/
│   ├── loader.py
│   └── platforms.yaml
├── test/
│   ├── __init__.py
│   ├── unit/
│   └── integration/
│       ├── test_compile.py
│       ├── test_deploy.py
│       ├── test_verify.py
│       ├── test_g720.py
│       ├── test_pipeline.py
│       └── test_mcp_basic.py
├── server.py
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

---

## Installation / 安装

推荐：

```text
Python 3.11
```

安装 Python 依赖：

```bash
pip install -r requirements.txt
```

当前主要依赖：

```text
mcp
onnx
pyyaml
```

Horizon 和 MediaTek 的芯片工具链不通过 `requirements.txt` 安装，需要独立准备对应 Docker / SDK 环境。

---

## Running MCP / 运行 MCP

基础入口：

```bash
python server.py
```

MCP Client 示例：

```python
import asyncio

from mcp import Client
from server import mcp


async def main():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "get_platform_info",
            {
                "platform": "g720",
            },
        )

        print(result.content)


asyncio.run(main())
```

---

## Example: G720 Pipeline

逻辑调用：

```python
deploy_pipeline(
    platform="g720",
    model_path="model_int8.tflite",
)
```

执行：

```text
model_int8.tflite
        │
        ▼
   ncc-tflite
        │
        ▼
 model_int8.dla
        │
        ▼
 deployment package
        │
        ▼
   G720 Board
        │
        ▼
    NeuronRT
        │
        ▼
 FPS / Latency
```

---

## Example: J6P Pipeline

逻辑调用：

```python
deploy_pipeline(
    platform="j6p",
    model_path="model.onnx",
)
```

执行：

```text
model.onnx
    │
    ▼
hb_config_generator
    │
    ▼
hb_compile
    │
    ▼
model.hbm
    │
    ▼
J6P Board
    │
    ▼
deployment verification
```

---

## Testing / 测试

建议从仓库根目录使用 Module 方式运行测试：

```bash
python -m test.integration.test_g720
```

不要直接：

```bash
python test/integration/test_g720.py
```

否则项目根目录可能没有进入 Python Module Search Path，导致：

```text
ModuleNotFoundError: No module named 'adapters'
```

### G720 Integration Test

```bash
python -m test.integration.test_g720
```

当前覆盖：

```text
get_platform_info
compile_model
deploy_model
verify_model
```

### Pipeline Integration Test

```bash
python -m test.integration.test_pipeline
```

当前验证：

```text
Compile
  ↓
Deploy
  ↓
Verify
```

---

## Current Verified Capabilities / 当前已验证能力

### Common

- [x] MCP Server
- [x] MCP Tool registration
- [x] Platform Registry
- [x] Base Adapter
- [x] Unified compile interface
- [x] Unified deploy interface
- [x] Unified verify interface
- [x] Unified deploy pipeline
- [x] Integration tests

### ONNX

- [x] ONNX loading
- [x] Input parsing
- [x] Output parsing
- [x] Shape parsing
- [x] Operator statistics
- [x] Opset parsing
- [x] Basic compatibility checking

### Horizon J6P

- [x] Real Docker toolchain
- [x] ONNX compile
- [x] Automatic config generation
- [x] HBM generation
- [x] Compile performance parsing
- [x] SCP deployment
- [x] Board artifact verification
- [ ] Real board inference
- [ ] Runtime benchmark
- [ ] Accuracy verification

### MediaTek G720

- [x] Real NeuroPilot SDK
- [x] INT8 TFLite compile
- [x] DLA generation
- [x] Deployment package
- [x] SCP deployment
- [x] Real board inference
- [x] Warmup
- [x] Benchmark
- [x] FPS parsing
- [x] Latency parsing
- [ ] Accuracy comparison
- [ ] Output postprocess validation

### Horizon X5

- [x] Adapter skeleton
- [ ] Real compile
- [ ] Real deployment
- [ ] Real board inference
- [ ] Benchmark

---

## Design Principles / 设计原则

### Unified API

不同芯片通过统一 MCP Tool 调用：

```text
compile_model
deploy_model
verify_model
deploy_pipeline
```

### Adapter Isolation

厂商工具链差异限制在：

```text
adapters/
```

MCP Server 不直接实现厂商命令。

### Real Verification

只有真实工具链或真实开发板验证过的能力才标记：

```text
Verified
```

### No Private Assets

仓库不提交：

- 私有 SDK
- 客户模型
- 客户数据
- 私有 Calibration 数据
- 内部工具
- 商业项目资产

### No Environment Leakage

代码中避免保存：

- 开发板真实 IP
- 用户名密码
- API Key
- Token
- SSH Private Key
- 内部服务器地址

### Automation First

重复部署操作尽量自动化：

```text
Model
  ↓
MCP
  ↓
Compile
  ↓
Deploy
  ↓
Verify
  ↓
Benchmark
  ↓
Report
```

---

## Roadmap / 后续计划

### Phase 1 — MCP Foundation

- [x] MCP Server
- [x] ONNX Inspection
- [x] Compatibility Check
- [x] Platform Adapter
- [x] Platform Registry

### Phase 2 — Real Platform Deployment

- [x] Horizon J6P
- [x] MediaTek G720
- [x] Unified `deploy_path`
- [x] Unified `deploy_pipeline`
- [x] Integration Test

### Phase 3 — Deployment Engineering

计划增加：

- [ ] Unified benchmark schema
- [ ] J6P real board inference
- [ ] Deployment report generation
- [ ] Structured error handling
- [ ] Timeout handling
- [ ] Compile cache
- [ ] Artifact metadata
- [ ] Output collection
- [ ] Accuracy verification

### Phase 4 — More Platforms

计划支持：

- [ ] Horizon X5
- [ ] MediaTek G5100
- [ ] Horizon J5
- [ ] Horizon S100
- [ ] Other edge AI platforms

只有完成真实验证后才会标记为 Verified。

### Phase 5 — Skill

MCP 基础设施稳定后增加 Edge Model Deployment Skill。

目标：

```text
User
 │
 │ "Deploy this model to G720"
 ▼
AI Agent
 │
 ▼
Deployment Skill
 │
 ├── inspect model
 ├── select platform
 ├── check compatibility
 ├── compile
 ├── deploy
 ├── verify
 ├── benchmark
 └── generate report
 │
 ▼
Edge Deploy MCP
```

MCP 负责：

```text
Tools / Actions
```

Skill 负责：

```text
Workflow / SOP / Decision Logic
```

---

## Future Direction / 长期方向

长期目标是支持更多模型和边缘 AI 芯片平台：

```text
PyTorch
ONNX
TFLite
Transformer
Vision Model
Audio Model
LLM / VLM
      │
      ▼
Edge Deploy MCP
      │
      ├── Horizon
      ├── MediaTek
      ├── Rockchip
      ├── Qualcomm
      └── Other Edge AI Platforms
      │
      ▼
Compile
Quantize
Deploy
Benchmark
Verify
Report
```

最终让 AI Agent 能够理解：

```text
模型是什么
目标芯片是什么
需要什么输入格式
需要什么量化方式
使用什么工具链
如何部署
如何验证
如何评估性能
```

并自动完成端侧模型部署流程。

---

## Security / 安全

不要提交：

```text
SSH passwords
Private keys
API keys
Access tokens
Internal server addresses
Private SDK packages
Customer models
Customer datasets
Private calibration datasets
Proprietary binaries
```

开发环境特有信息应通过：

```text
Local configuration
Environment variables
SSH aliases
Ignored files
```

进行管理。

---

## Contributing / 贡献

新增平台建议遵循：

```text
1. Create adapter
2. Implement BasePlatformAdapter
3. Add platform configuration
4. Register adapter
5. Test compile
6. Test board deployment
7. Test runtime verification
8. Add integration test
9. Update README
10. Mark Verified only after real validation
```

不要仅根据厂商文档直接将平台标记为 Verified。

---

## License / 开源协议

This project is licensed under the Apache License 2.0.

本项目采用 Apache License 2.0 开源协议。
