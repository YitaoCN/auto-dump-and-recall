#!/usr/bin/env python3
"""
上下文会话存储脚本

将会话摘要持久化为 JSON 文件到 {workspace}/.context-sessions/ 目录。

用法：
  python3 store_session.py --session-id <id> --workspace <workspace> --content <content>
  python3 store_session.py --session-id <id> --workspace <workspace> --content-file <path>

参数：
  --session-id    会话标识（建议格式：YYYYMMDD-HHmmss）
  --workspace     工作区路径
  --content       要存储的摘要内容（Markdown 格式字符串）
  --content-file  从文件读取摘要内容（与 --content 二选一）
  --decisions     关键决策（逗号分隔，可选）
  --files         修改过的文件（逗号分隔，可选）
  --next-steps    下一步/待办（逗号分隔，可选）
  --tags          标签（逗号分隔，可选）
"""

import argparse
import json
import os
import sys
from datetime import datetime

MAX_SESSIONS = 20


def store_session(session_id, workspace, content, decisions=None,
                  files=None, next_steps=None, tags=None):
    sessions_dir = os.path.join(workspace, '.context-sessions')
    os.makedirs(sessions_dir, exist_ok=True)

    record = {
        "session_id": session_id,
        "started_at": datetime.now().isoformat(),
        "stored_at": datetime.now().isoformat(),
        "summary": content.strip(),
        "key_decisions": [d.strip() for d in (decisions or []) if d.strip()],
        "files_modified": [f.strip() for f in (files or []) if f.strip()],
        "next_steps": [s.strip() for s in (next_steps or []) if s.strip()],
        "tags": [t.strip() for t in (tags or []) if t.strip()],
    }

    filepath = os.path.join(sessions_dir, f"{session_id}.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(record, f, ensure_ascii=False, indent=2)

    # 清理超出上限的旧会话
    _cleanup(sessions_dir, MAX_SESSIONS)

    return {"success": True, "path": filepath, "session_id": session_id}


def _cleanup(sessions_dir, max_keep):
    files = sorted(
        [f for f in os.listdir(sessions_dir) if f.endswith('.json')],
        reverse=True
    )
    for f in files[max_keep:]:
        os.remove(os.path.join(sessions_dir, f))


def main():
    parser = argparse.ArgumentParser(description='存储会话上下文摘要')
    parser.add_argument('--session-id', required=True, help='会话标识')
    parser.add_argument('--workspace', required=True, help='工作区路径')
    parser.add_argument('--content', default=None, help='摘要内容')
    parser.add_argument('--content-file', default=None, help='从文件读取摘要')
    parser.add_argument('--decisions', default=None, help='关键决策（逗号分隔）')
    parser.add_argument('--files', default=None, help='修改的文件（逗号分隔）')
    parser.add_argument('--next-steps', default=None, help='下一步（逗号分隔）')
    parser.add_argument('--tags', default=None, help='标签（逗号分隔）')

    args = parser.parse_args()

    content = args.content
    if args.content_file:
        with open(args.content_file, 'r', encoding='utf-8') as f:
            content = f.read()

    if not content:
        print("错误：必须提供 --content 或 --content-file", file=sys.stderr)
        sys.exit(1)

    result = store_session(
        session_id=args.session_id,
        workspace=args.workspace,
        content=content,
        decisions=args.decisions.split(',') if args.decisions else None,
        files=args.files.split(',') if args.files else None,
        next_steps=args.next_steps.split(',') if args.next_steps else None,
        tags=args.tags.split(',') if args.tags else None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
