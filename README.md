# Edge Deploy MCP

**基于 MCP 的边缘 AI 模型自动化部署框架**  
**An MCP-based framework for automated edge AI model deployment.**

Edge Deploy MCP provides a unified interface for edge AI model analysis, compilation, deployment, and verification across different hardware platforms.

Edge Deploy MCP 为不同边缘 AI 芯片平台提供统一的模型分析、编译、部署和验证流程。


---

# Overview / 项目简介

Edge Deploy MCP is designed to simplify the deployment workflow of deep learning models on edge AI chips.

Edge Deploy MCP 用于简化深度学习模型在边缘 AI 芯片上的部署流程。

The framework abstracts different hardware toolchains through platform adapters, enabling a unified deployment workflow.

框架通过平台 Adapter 层屏蔽不同芯片厂商工具链差异，实现统一部署流程。


Current supported workflow:

当前支持流程：

```
ONNX Model
    |
    v
Model Inspection
    |
    v
Compatibility Check
    |
    v
Platform Compilation
    |
    v
Edge Board Deployment
    |
    v
Deployment Verification
```


---

# Features / 功能特性

## Model Analysis / 模型分析

- ONNX model structure inspection  
  ONNX 模型结构分析

- Input and output tensor information  
  输入输出张量信息

- Operator statistics  
  算子统计信息

- ONNX opset compatibility checking  
  ONNX opset 兼容性检查


## Model Deployment / 模型部署

- Automated model compilation  
  自动模型编译

- Hardware-specific deployment pipeline  
  面向硬件平台的部署流程

- Board-side model verification  
  板端模型验证


## Platform Adapter Architecture / 平台适配架构

Support multiple AI chips through independent adapters.

通过独立 Adapter 支持不同 AI 芯片平台。


---

# Architecture / 系统架构


```
                    MCP Client
                        |
                        |
                Edge Deploy MCP
                        |
        +---------------+---------------+
        |                               |
        |                               |
  Model Tools                    Platform Adapter
        |                               |
        |                               |
 inspect_onnx                  Horizon J6P
 compile_model                 Horizon X5
 deploy_model                  MTK G720
 verify_model
```


---

# Project Structure / 项目结构


```
edge-deploy-mcp/

├── server.py                    # MCP server entry / MCP服务入口
│
├── adapters/                    # Platform adapters / 平台适配层
│   │
│   ├── base.py                  # Adapter interface / Adapter接口
│   ├── registry.py              # Adapter registry / Adapter注册管理
│   │
│   └── horizon/
│       ├── j6p.py               # Horizon J6P adapter
│       ├── x5.py                # Horizon X5 adapter
│       └── utils.py             # Horizon utilities
│
├── config/
│   ├── platforms.yaml           # Hardware configuration / 硬件配置
│   └── loader.py                # Config loader / 配置加载
│
├── tools/                       # MCP tools / MCP工具
│
├── test/
│   ├── unit/                    # Unit tests / 单元测试
│   │
│   └── integration/             # Hardware integration tests / 硬件集成测试
│
├── requirements.txt
└── README.md
```


---

# Supported Platforms / 支持平台


| Platform 平台 | Status 状态 | Description 描述 |
|---|---|---|
| Horizon J6P | ✅ Supported | ONNX compile / deploy / verify |
| Horizon X5 | 🚧 Adapter ready | Adapter structure prepared |
| MTK G720 | 🚧 Planned | MDLA deployment support |


---

# Deployment Workflow / 部署流程


## 1. Model Inspection / 模型分析


Analyze ONNX model information.

分析 ONNX 模型信息。


```
ONNX Model
      |
      v
inspect_onnx
      |
      v
Model Information
```


Output includes:

输出包括：

- Input / Output shape
- Operator statistics
- Opset version


---

## 2. Model Compilation / 模型编译


Example: Horizon J6P

示例：地平线 J6P


```
ONNX
 |
 hb_config_generator
 |
 hb_compile
 |
 model.hbm
```


Example result:

示例结果：

```json
{
  "status": "success",
  "platform": "J6P",
  "hbm_path": "model.hbm",
  "fps": 1335.63,
  "latency_us": 748.7
}
```


---

## 3. Model Deployment / 模型部署


Deploy compiled model to edge board.

将编译后的模型部署到边缘设备。


```
model.hbm
     |
     v
 SCP Transfer
     |
     v
Edge Board
```


Example:

示例：

```json
{
  "status": "success",
  "remote_path": "/root/hehailong/mcp_test/model.hbm"
}
```


---

## 4. Deployment Verification / 部署验证


Verify deployed model on target device.

验证目标设备上的模型。


```
MCP
 |
 SSH
 |
Target Board
 |
Model Check
```


---

# Configuration Management / 配置管理


All hardware-specific information is stored in:

所有硬件相关信息统一存储于：

```
config/platforms.yaml
```


Example:

示例：

```yaml
horizon:
  j6p:
    container: hhl_j6_391
    ssh_host: j6p
    march: nash-p
    mount_root: /data/users/example/horizon_models
    remote_dir: /root/model
```


The source code does not contain hardware-specific configuration.

代码中不保存具体硬件环境信息。


---

# Installation / 安装


Create Python environment:

创建 Python 环境：


```bash
conda create -n mcp python=3.11

conda activate mcp
```


Install dependencies:

安装依赖：


```bash
pip install -r requirements.txt
```


---

# Testing / 测试


## Basic MCP Test / 基础 MCP 测试


```bash
python test/integration/test_mcp_basic.py
```


## Compile Test / 编译测试


```bash
python test/integration/test_compile.py
```


## Deploy Test / 部署测试


```bash
python test/integration/test_deploy.py
```


## Verify Test / 验证测试


```bash
python test/integration/test_verify.py
```


---

# Roadmap / 后续计划


## Platform Support / 平台支持

- [x] Horizon J6P
- [ ] Horizon X5
- [ ] MTK G720
- [ ] MTK G5100


## Deployment Capability / 部署能力

- [x] ONNX inspection / ONNX分析
- [x] Compatibility checking / 兼容性检查
- [x] Model compilation / 模型编译
- [x] HBM deployment / HBM部署
- [x] Board verification / 板端验证
- [ ] Runtime inference
- [ ] Performance benchmark report


---


# License / 开源协议

This project is licensed under the Apache License 2.0.

本项目采用 Apache License 2.0 开源协议。