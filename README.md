# context-session-manager

> 自动管理长对话的上下文存储与召回，实现跨会话记忆连续性。

一个 WPS 灵犀 (Lingxi) Agent Skill。当对话轮次增多导致上下文窗口接近饱和时，自动将会话摘要和关键状态持久化到文件系统；当用户发送 `/new` 或新会话开始时，自动检索并召回上一个会话的上下文摘要。

## 工作原理

两阶段循环：

1. **存储**：每次对话时检测上下文长度，接近饱和时自动生成会话摘要并持久化为 JSON
2. **召回**：用户发送 `/new` 或检测到新会话时，自动检索最近的会话摘要并注入上下文

## 触发条件

### 存储触发（满足任一）

- 对话轮次 >= 8 轮
- 当前会话包含代码提交、文件创建、架构决策等高价值操作
- 用户明确要求"记住"/"保存"等意图

### 召回触发

- 用户消息为 `/new`、"新会话"、"重新开始"等
- 用户说"上次我们聊到..."、"继续之前的工作"等

## 文件结构

```
context-session-manager/
├── SKILL.md                        # 技能定义（frontmatter + 工作流说明）
├── references/
│   └── session-format.md           # 会话 JSON 格式规范 + 摘要生成最佳实践
└── scripts/
    ├── store_session.py            # 存储脚本：持久化会话摘要
    └── recall_session.py           # 召回脚本：按时间/标签检索历史会话
```

## 使用方式

### 存储会话

```bash
python3 scripts/store_session.py \
  --session-id 20260430-153000 \
  --workspace /path/to/workspace \
  --content "## 会话摘要
完成调研报告..." \
  --decisions "L1+L2两级架构" \
  --files "research.md" \
  --tags "orchclaw,调研"
```

### 召回会话

```bash
# 列出最近 3 个会话摘要
python3 scripts/recall_session.py --workspace /path/to/workspace --limit 3

# 获取最近 1 个会话的完整内容
python3 scripts/recall_session.py --workspace /path/to/workspace --latest

# 按标签过滤
python3 scripts/recall_session.py --workspace /path/to/workspace --tags "orchclaw"
```

### 在 WPS 灵犀中使用

将本仓库内容放入技能目录：

```
~/.wps-lingxi/skills/context-session-manager/
```

新会话启动后，当对话轮次增多或用户发送 `/new` 时，技能自动生效。

## 存储格式

会话摘要以 JSON 格式存储在 `{workspace}/.context-sessions/` 目录下：

```json
{
  "session_id": "20260430-153000",
  "started_at": "2026-04-30T15:30:00",
  "stored_at": "2026-04-30T16:45:00",
  "summary": "完成调研报告，产出 research.md...",
  "key_decisions": ["L1+L2两级架构"],
  "files_modified": ["research.md"],
  "next_steps": ["实现流式响应协议"],
  "tags": ["orchclaw", "调研"]
}
```

- 最多保留 20 个会话文件，超出自动清理
- 支持按标签过滤召回

## 设计理念

| 维度 | 说明 |
|------|------|
| 会话级记忆 | 文件存储，适合单次任务的断点续作 |
| 长期记忆 | 配合 `get_memory` / `write_memory` 管理用户画像等跨会话持久信息 |
| 存储位置 | `{workspace}/.context-sessions/`，不污染工作区 |
| 安全 | 不存储密码、密钥、Token 等敏感信息 |

## License

MIT
