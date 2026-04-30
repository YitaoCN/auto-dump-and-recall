# 上下文会话存储规范

## 会话摘要 JSON 格式

每个会话存储为一个 JSON 文件，文件名为 `{session_id}.json`。

```json
{
  "session_id": "20260430-153000",
  "started_at": "2026-04-30T15:30:00.000000",
  "stored_at": "2026-04-30T16:45:00.000000",
  "summary": "## 会话摘要\n\n用户完成了 OrchClaw 实时响应架构调研报告。\n\n### 已完成\n- 产出文件: orchclaw-realtime-response-research.md\n- 关键决策: L1+L2 两级架构（去掉本地模型）\n\n### 下一步\n- 实现流式响应协议\n- 消息优先级队列",
  "key_decisions": [
    "L1即时层+L2远程LLM两级架构",
    "去掉本地模型方案"
  ],
  "files_modified": [
    "orchclaw-realtime-response-research.md"
  ],
  "next_steps": [
    "实现流式响应协议",
    "消息优先级队列"
  ],
  "tags": [
    "orchclaw",
    "调研",
    "实时响应"
  ]
}
```

## 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| session_id | string | 是 | 会话标识，建议格式 `YYYYMMDD-HHmmss` |
| started_at | string | 是 | 会话开始时间（ISO 8601） |
| stored_at | string | 是 | 存储时间（ISO 8601） |
| summary | string | 是 | Markdown 格式摘要，200-500 字 |
| key_decisions | string[] | 否 | 关键决策列表 |
| files_modified | string[] | 否 | 修改过的文件列表 |
| next_steps | string[] | 否 | 待办/下一步列表 |
| tags | string[] | 否 | 标签，用于召回过滤 |

## 存储位置

```
{workspace}/.context-sessions/
├── 20260429-140000.json
├── 20260430-090000.json
├── 20260430-153000.json
└── ...
```

- 最多保留 20 个会话文件
- 超出时自动清理最早的文件
- 目录以 `.` 开头，不污染工作区文件列表

## 摘要生成最佳实践

### 结构模板

```markdown
## 会话摘要

### 任务目标
用户要求 [具体任务]

### 已完成
- [完成事项 1]
- [完成事项 2]

### 关键决策
- [决策 1 及原因]
- [决策 2 及原因]

### 当前状态
[做到哪一步，是否有未完成的部分]

### 下一步
- [待办 1]
- [待办 2]
```

### 标签提取规则

从会话内容中自动提取标签，优先级：
1. **项目名**：如 `orchclaw`、`frontend-redesign`
2. **任务类型**：如 `调研`、`开发`、`部署`、`调试`
3. **技术关键词**：如 `实时响应`、`WebSocket`、`LLM`
4. **文件格式**：如 `pptx`、`xlsx`、`pdf`

每个会话 2-5 个标签。

### 摘要质量检查

生成摘要后自检：
- 是否能让新会话的 agent 理解"上次做了什么"
- 是否包含关键的文件路径和决策理由
- 是否明确标注了"未完成"的部分
- 是否控制在 500 字以内
