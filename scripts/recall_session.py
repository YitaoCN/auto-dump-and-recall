#!/usr/bin/env python3
"""
上下文会话召回脚本

从 {workspace}/.context-sessions/ 目录检索最近的会话摘要。

用法：
  python3 recall_session.py --workspace <workspace> [--limit 3] [--tags tag1,tag2]

参数：
  --workspace   工作区路径
  --limit       召回最近 N 个会话（默认 3）
  --tags        按标签过滤（逗号分隔，可选，匹配任一标签即命中）
  --latest      仅返回最近 1 个会话的完整内容（默认输出列表摘要）
"""

import argparse
import json
import os
import sys


def recall_sessions(workspace, limit=3, tags=None):
    sessions_dir = os.path.join(workspace, '.context-sessions')
    if not os.path.exists(sessions_dir):
        return {"sessions": [], "total": 0}

    files = sorted(
        [f for f in os.listdir(sessions_dir) if f.endswith('.json')],
        reverse=True
    )

    results = []
    tag_set = set(t.strip().lower() for t in (tags or [])) if tags else None

    for filename in files:
        filepath = os.path.join(sessions_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                record = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        # 标签过滤
        if tag_set:
            record_tags = set(t.lower() for t in record.get('tags', []))
            if not tag_set.intersection(record_tags):
                continue

        # 输出精简版（不包含完整 summary，减少返回体积）
        results.append({
            "session_id": record.get("session_id"),
            "stored_at": record.get("stored_at"),
            "summary_preview": (record.get("summary", "")[:200] + "...") if len(record.get("summary", "")) > 200 else record.get("summary", ""),
            "key_decisions": record.get("key_decisions", []),
            "files_modified": record.get("files_modified", []),
            "next_steps": record.get("next_steps", []),
            "tags": record.get("tags", []),
            "file": filepath,
        })

        if len(results) >= limit:
            break

    return {"sessions": results, "total": len(results)}


def recall_latest(workspace, tags=None):
    """召回最近 1 个会话的完整内容"""
    result = recall_sessions(workspace, limit=1, tags=tags)
    if not result["sessions"]:
        return None

    session_file = result["sessions"][0].get("file")
    if not session_file or not os.path.exists(session_file):
        return None

    try:
        with open(session_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def main():
    parser = argparse.ArgumentParser(description='召回会话上下文摘要')
    parser.add_argument('--workspace', required=True, help='工作区路径')
    parser.add_argument('--limit', type=int, default=3, help='召回数量（默认 3）')
    parser.add_argument('--tags', default=None, help='标签过滤（逗号分隔）')
    parser.add_argument('--latest', action='store_true', help='仅返回最近 1 个完整内容')

    args = parser.parse_args()

    if args.latest:
        result = recall_latest(args.workspace, args.tags)
        if result:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({"session": None, "message": "没有找到可召回的会话"}))
    else:
        result = recall_sessions(args.workspace, args.limit, args.tags)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
