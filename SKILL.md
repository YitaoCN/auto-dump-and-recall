---
name: context-session-manager
description: 自动管理长对话的上下文存储与召回。当对话轮次增多导致上下文窗口接近饱和时，自动将会话摘要和关键状态持久化到文件系统；当用户发送 /new 或新会话开始时，自动检索并召回上一个会话的上下文摘要，实现跨会话记忆连续性。适用于：长时间多轮对话、需要断点续作的开发任务、跨会话保持项目上下文的场景。触发关键词：上下文存储、会话管理、/new、新会话、断点续作、上下文召回、会话摘要、新对话、继续之前。
---

# 上下文会话管理器

## 核心规则

本技能的指令是**确定性执行指令**，不是可选建议。满足触发条件时必须执行，不得跳过。

## 触发钩子

### 钩子 A：会话结束前自动存储（必执行）

**触发条件**（满足任一即触发）：

1. 对话轮次（用户消息数）>= 8 轮
2. 当前会话产生了文件、代码、报告等可交付物
3. 当前会话包含架构决策、技术选型等高价值结论
4. 用户明确说"记住"、"保存"、"存一下"

**执行时机**：在生成最终回复之前（即回复内容写完后、调用工具输出之前），先执行存储。

**执行步骤**（严格按此顺序）：

1. 用 `jupyter_cell_exec` 执行以下代码，创建会话目录并写入摘要：

```python
import os, json
from datetime import datetime

cwd = os.getcwd()
session_dir = os.path.join(cwd, '.context-sessions')
os.makedirs(session_dir, exist_ok=True)

session_id = datetime.now().strftime('%Y%m%d-%H%M%S')

# === 在此处替换为实际摘要内容 ===
summary = """
[在此处写入 3-8 句话的会话摘要]
- 任务目标：用户要求做什么
- 已完成：做了什么，产出了哪些文件/代码
- 关键决策：做了哪些技术选型
- 当前状态：做到哪一步，是否有未完成的部分
- 下一步：还有什么没做
"""

record = {
    "session_id": session_id,
    "stored_at": datetime.now().isoformat(),
    "summary": summary.strip(),
    "key_decisions": [],
    "files_modified": [],
    "next_steps": [],
    "tags": []
}

filepath = os.path.join(session_dir, session_id + '.json')
with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(record, f, ensure_ascii=False, indent=2)

# 清理：只保留最近 20 个
import glob
files = sorted(glob.glob(os.path.join(session_dir, '*.json')))
if len(files) > 20:
    for old in files[:-20]:
        os.remove(old)

print("STORED:" + session_id + " at " + filepath)
```

2. 在上面的代码中，将 `summary`、`key_decisions`、`files_modified`、`next_steps`、`tags` 替换为当前会话的实际内容。

3. 正常回复用户，不需要告知用户存储动作（静默执行）。

### 钩子 B：新会话自动召回（必执行）

**触发条件**（满足任一即触发）：

1. 用户消息为 `/new` 或"新会话"、"重新开始"、"继续之前的工作"、"上次我们聊到"
2. 对话开头检测到 `.context-sessions/` 目录存在且有历史会话文件

**执行步骤**：

1. 用 `jupyter_cell_exec` 执行以下代码：

```python
import os, json, glob

cwd = os.getcwd()
session_dir = os.path.join(cwd, '.context-sessions')

if not os.path.exists(session_dir):
    print("NO_SESSIONS")
else:
    files = sorted(glob.glob(os.path.join(session_dir, '*.json')), reverse=True)[:3]
    if not files:
        print("NO_SESSIONS")
    else:
        sessions = []
        for f in files:
            with open(f, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
            sessions.append({
                "id": data.get("session_id"),
                "time": data.get("stored_at"),
                "summary": data.get("summary", ""),
                "decisions": data.get("key_decisions", []),
                "files": data.get("files_modified", []),
                "next_steps": data.get("next_steps", []),
                "tags": data.get("tags", [])
            })
        print(json.dumps(sessions, ensure_ascii=False, indent=2))
```

2. 读取召回结果。如果输出 `NO_SESSIONS`，跳过后续步骤。

3. 将召回的摘要注入当前上下文，并在回复中告知用户：

> 已召回最近会话上下文（{时间}），上次完成了 {摘要要点}。需要继续吗？

4. 用户确认继续后，基于召回的上下文恢复工作状态。

## 摘要生成规则

摘要必须包含以下要素（按重要性排序）：

1. **任务目标**：用户要做什么
2. **已完成**：做了什么、产生了哪些文件/代码（写完整路径）
3. **关键决策**：做了哪些技术选型或方案选择
4. **当前状态**：做到哪一步、是否有未完成的部分
5. **下一步**：还有什么没做

摘要长度控制在 200-500 字。用 Markdown 列表格式。

标签提取规则：从会话内容中提取 2-5 个标签，优先级为项目名 > 任务类型（调研/开发/部署） > 技术关键词。

## 注意事项

- 存储目录 `.context-sessions/` 以 `.` 开头，不污染工作区
- 摘要中不包含密码、密钥、Token 等敏感信息
- 存储动作静默执行，不告知用户（召回时才告知）
- 如果 `os.getcwd()` 返回临时目录，改用 `/Users/yitao/Desktop` 作为 fallback
