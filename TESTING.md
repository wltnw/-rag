# RAG智能问答系统测试文档

## 测试概述

本文档描述了RAG智能问答系统的测试策略、测试用例和运行方法。

## 测试架构

### 测试分层

```
┌─────────────────────────────────────────┐
│           AI质量测试                     │
│    (答案准确性、幻觉检测)                │
├─────────────────────────────────────────┤
│           接口测试                       │
│    (API端点、错误处理、边界条件)         │
├─────────────────────────────────────────┤
│           检索测试                       │
│    (知识库检索、相关性、上下文)          │
└─────────────────────────────────────────┘
```

### 测试文件说明

| 文件名 | 测试类型 | 测试内容 |
|--------|----------|----------|
| `conftest.py` | 配置文件 | 测试fixtures和通用工具 |
| `test_api_endpoints.py` | 接口测试 | FastAPI端点功能测试 |
| `test_retrieval.py` | 检索测试 | 知识库检索准确性测试 |
| `test_error_handling.py` | 异常测试 | 边界条件和异常处理 |
| `test_ai_quality.py` | AI质量测试 | 答案准确性和幻觉检测 |

## 测试环境准备

### 1. 安装测试依赖

```bash
pip install -r requirements_test.txt
```

### 2. 启动API服务

```bash
python run_server.py
```

### 3. 验证服务状态

```bash
curl http://localhost:8000/health
```

## 运行测试

### 运行所有测试

```bash
pytest
```

### 运行特定测试文件

```bash
# 运行API接口测试
pytest test_api_endpoints.py

# 运行AI质量测试
pytest test_ai_quality.py
```

### 运行带标记的测试

```bash
# 运行所有API测试
pytest -m api

# 运行所有AI质量测试
pytest -m ai_quality
```

### 并行运行测试

```bash
# 使用pytest-xdist并行运行
pytest -n auto

# 指定进程数
pytest -n 4
```

### 生成测试报告

```bash
# 生成HTML报告
pytest --html=report.html

# 生成覆盖率报告
pytest --cov=. --cov-report=html

# 生成Allure报告
pytest --alluredir=allure-results
allure serve allure-results
```

## 测试用例详解

### API接口测试

#### 健康检查测试
- 验证 `/health` 端点返回正确状态
- 检查响应时间在合理范围内

#### 问答接口测试
- 测试有效问题的响应
- 验证响应结构完整性
- 测试不同意图的问题
- 验证来源类型

#### 文档接口测试
- 测试Swagger文档可访问性
- 验证OpenAPI schema正确性

### 检索测试

#### 检索准确性测试
- 水泵维护信息检索
- 传感器电压信息检索
- 风扇启动温度检索
- 故障代码信息检索

#### 检索相关性测试
- 验证找到相关来源
- 测试无关问题处理
- 多次检索一致性

#### 检索上下文测试
- 上下文质量验证
- 上下文完整性验证

### AI质量测试

#### 答案准确性测试
- 水泵维护答案准确性
- 传感器电压答案准确性
- 风扇启动温度准确性
- 故障代码答案准确性

#### 幻觉检测测试
- 未知问题幻觉检测
- 技术问题幻觉检测
- 数字信息幻觉检测

### 异常和边界测试

#### 输入验证测试
- 空问题处理
- 空白问题处理
- 缺少字段处理
- null值处理

#### 边界条件测试
- 超长问题处理
- 特殊字符处理
- Unicode字符处理
- 纯数字问题处理

#### 错误恢复测试
- 快速连续请求
- 无效JSON格式
- 错误Content-Type

## 测试数据

### 测试问题集

#### 基础问题
1. "水泵需要多久维护一次？"
2. "大棚里温度多少度的时候需要启动风扇？"
3. "温湿度传感器的电源电压范围是多少？"
4. "DHT22 传感器的温度测量精度是多少？"
5. "ERR_002 是什么故障？应该怎么处理？"
6. "DHT22 和 SHT31 这两个传感器成本差多少？"

#### 边界问题
1. "" (空问题)
2. "   " (空白问题)
3. "a" * 1000 (超长问题)
4. "!@#$%^&*()" (特殊字符)
5. "1234567890" (纯数字)

#### 异常问题
1. "火星上的农场怎么管理？" (无关问题)
2. "量子计算机如何优化农场管理？" (超出范围)
3. "水泵的价格是多少？" (知识库中没有)

## 测试指标

### 功能指标
- API端点响应正常
- 错误处理正确
- 边界条件处理合理

### AI质量指标
- 答案准确性: > 80%
- 幻觉检测: 能识别未知问题

## 测试最佳实践

### 1. 测试前准备
- 确保API服务已启动
- 检查测试数据完整性
- 验证测试环境配置

### 2. 测试执行
- 按顺序运行测试
- 记录测试结果
- 分析失败原因

### 3. 测试后分析
- 生成测试报告
- 分析性能瓶颈
- 记录改进建议

### 4. 持续集成
- 配置CI/CD流水线
- 自动化测试执行
- 测试结果通知

## 故障排除

### 常见问题

#### 1. API服务未启动
```
错误: Connection refused
解决: 运行 python run_server.py 启动服务
```

#### 2. 测试依赖缺失
```
错误: ModuleNotFoundError
解决: pip install -r requirements_test.txt
```

#### 3. 测试超时
```
错误: Timeout
解决: 检查网络连接，增加超时时间
```

#### 4. 测试数据问题
```
错误: AssertionError
解决: 检查知识库数据，验证测试预期
```

## 测试报告示例

### 测试摘要
```
========================= test session starts ==========================
platform win32 -- Python 3.11.0, pytest-7.4.0
collected 50 items

test_api_endpoints.py::TestHealthEndpoints::test_health_check PASSED
test_api_endpoints.py::TestAskEndpoint::test_ask_valid_question PASSED
test_retrieval.py::TestRetrievalAccuracy::test_pump_maintenance_retrieval PASSED
test_error_handling.py::TestInputValidation::test_empty_question PASSED
test_ai_quality.py::TestAnswerAccuracy::test_pump_maintenance_accuracy PASSED
test_ai_quality.py::TestHallucinationDetection::test_no_hallucination_for_unknown PASSED

========================= 50 passed in 60.12s ==========================
```

### 覆盖率报告
```
Name                     Stmts   Miss  Cover   Missing
------------------------------------------------------
rag_api_improved.py        150     15    90%   45-50, 78-82
conftest.py                 85      5    94%   120-125
------------------------------------------------------
TOTAL                      235     20    91%
```

## 扩展测试

### 添加新测试用例

1. 在相应测试文件中添加测试函数
2. 使用pytest标记分类测试
3. 更新测试文档

### 自定义测试工具

1. 在 `conftest.py` 中添加fixtures
2. 创建测试辅助类
3. 实现测试数据生成器

## 总结

本测试套件覆盖了RAG智能问答系统的各个层面，包括：

1. **功能测试**: 验证系统基本功能
2. **接口测试**: 确保API端点正确性
3. **边界测试**: 测试异常和边界条件
4. **检索测试**: 验证知识库检索准确性
5. **AI质量测试**: 验证答案准确性和幻觉检测

通过全面的测试，确保系统在生产环境中稳定可靠地运行。