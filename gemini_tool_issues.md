# Gemini 模型工具兼容性问题说明

## 🚨 遇到的错误

### 错误 1: Function calling with response mime type 'application/json' is unsupported
**原因：** Gemini 不支持同时使用工具调用和结构化输出（`output_schema`）

**解决方案：**
- 移除 `output_schema` 参数
- 在 `instructions` 中明确输出格式要求

```python
# ❌ 错误
Team(
    model=Gemini(...),
    tools=[...],
    output_schema=Article  # 与工具冲突
)

# ✅ 正确
Team(
    model=Gemini(...),
    tools=[...],
    instructions=[
        "按以下格式输出：",
        "- 标题：...",
        "- 摘要：...",
    ]
)
```

---

### 错误 2: property is not defined in required
**原因：** 工具的参数定义不符合 Gemini 的要求

**可能的原因：**
1. 使用了 `**kwargs` 参数
2. `required` 字段引用了未定义的属性
3. 某些工具（如 ReasoningTools）与 Gemini 不兼容

**解决方案：**

#### 方案 1：修改自定义工具（移除 **kwargs）
```python
# ❌ 可能有问题
def email_user(self, subject: str, body: str, **kwargs) -> str:
    ...

# ✅ 推荐
def email_user(self, subject: str, body: str) -> str:
    ...
```

#### 方案 2：避免使用某些工具
```python
# ❌ ReasoningTools 可能与 Gemini 不兼容
tools=[
    ReasoningTools(),  # 可能导致错误
    CEmailTools(...),
]

# ✅ 只使用兼容的工具
tools=[
    CEmailTools(...),
    DuckDuckGoTools(),
]
```

---

### 错误 3: 503 UNAVAILABLE - Model is overloaded
**原因：** Gemini API 服务器过载

**解决方案：**
1. 稍后重试
2. 添加重试机制
3. 考虑使用付费 API 获得更好的可用性

```python
# 添加重试配置（如果 Agno 支持）
Agent(
    model=Gemini(...),
    retries=3,  # 重试次数
    delay_between_retries=2,  # 重试间隔（秒）
    exponential_backoff=True,  # 指数退避
)
```

---

## 🎯 Gemini 模型使用建议

### 1. 工具选择
**兼容性好的工具：**
- ✅ `DuckDuckGoTools`
- ✅ `HackerNewsTools`
- ✅ `Newspaper4kTools`
- ✅ 简单的自定义工具（无 **kwargs）

**可能有问题的工具：**
- ⚠️ `ReasoningTools`（参数定义可能不兼容）
- ⚠️ `MCPTools`（某些配置）
- ⚠️ 带有 `**kwargs` 的自定义工具

### 2. 结构化输出
**不要同时使用：**
- ❌ `tools` + `output_schema`
- ❌ `tools` + `structured_outputs=True`

**替代方案：**
- ✅ 使用 `instructions` 指定输出格式
- ✅ 使用 `expected_output` 描述期望
- ✅ 使用 `markdown=True` 获得格式化输出

### 3. 最佳实践

```python
# ✅ 推荐的 Gemini Agent 配置
agent = Agent(
    model=Gemini(
        id="gemini-2.5-flash",
        api_key="your-api-key"
    ),
    
    # 使用 instructions 而不是 output_schema
    instructions=[
        "仔细分析问题",
        "使用工具获取信息",
        "按以下格式输出结果：...",
    ],
    
    # 只使用兼容的工具
    tools=[
        DuckDuckGoTools(),
        # 自定义工具（无 **kwargs）
    ],
    
    # 其他配置
    add_datetime_to_context=True,
    markdown=True,
    
    # 添加重试机制
    retries=3,
    delay_between_retries=2,
)
```

---

## 🔍 调试技巧

### 1. 启用调试模式
```python
Agent(
    debug_mode=True,  # 查看详细日志
)
```

### 2. 逐个测试工具
```python
# 先测试单个工具
tools=[CEmailTools(...)]  # 测试邮件工具

# 再逐步添加
tools=[
    CEmailTools(...),
    DuckDuckGoTools(),  # 添加搜索工具
]
```

### 3. 查看工具定义
```python
# 打印工具的函数签名
from agno.tools import get_function_schema

for tool in agent.tools:
    schema = get_function_schema(tool)
    print(schema)
```

---

## 📊 模型对比

| 功能 | Gemini | OpenAI | Claude |
|------|--------|--------|--------|
| 工具调用 | ✅ | ✅ | ✅ |
| 结构化输出 | ✅ | ✅ | ✅ |
| 工具+结构化 | ❌ | ✅ | ✅ |
| **kwargs 支持 | ⚠️ | ✅ | ✅ |
| 免费额度 | ✅ 高 | ⚠️ 低 | ⚠️ 低 |

---

## 💡 建议

1. **如果需要结构化输出 + 工具**：考虑使用 OpenAI 或 Claude
2. **如果使用 Gemini**：避免同时使用工具和 output_schema
3. **自定义工具**：避免使用 `**kwargs`，明确定义所有参数
4. **测试**：在生产环境前充分测试工具兼容性

