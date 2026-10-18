#!/usr/bin/env python3
"""Create a design project without replacing existing files or following links."""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import stat
import sys
from pathlib import Path


DIRECTORIES = (
    "00_核心分区",
    "01_素材库",
    "01_素材库/图片",
    "01_素材库/视频",
    "01_素材库/文档",
    "01_素材库/链接",
    "02_过滤库",
    "02_过滤库/已通过",
    "02_过滤库/待核实",
    "02_过滤库/未采用",
    "03_制作区",
    "04_最终方案",
    "05_成品",
)


def _is_link(path: Path) -> bool:
    junction = getattr(path, "is_junction", lambda: False)
    if path.is_symlink() or junction():
        return True
    # Python 3.10/3.11 on Windows has no Path.is_junction().
    if os.name == "nt":
        try:
            return bool(path.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
        except FileNotFoundError:
            pass
    return False


def _validate_destination(root: Path, relative: str, directory: bool) -> None:
    target = root / relative
    for part in (target, *target.parents):
        if part == root.parent:
            break
        if _is_link(part):
            raise ValueError(f"计划路径包含符号链接或联接目录，请选择独立项目目录：{part}")
    if not target.resolve().is_relative_to(root):
        raise ValueError(f"计划路径超出项目目录：{target}")
    if target.exists() and target.is_dir() != directory:
        expected = "目录" if directory else "文件"
        raise ValueError(f"路径类型冲突，应该是{expected}：{target}")


def _initial_files(name: str, project_type: str) -> dict[str, tuple[str, str]]:
    progress = {
        "schema_version": 1,
        "project_name": name,
        "project_type": project_type,
        "stage": "brief",
        "direction_confirmed": False,
        "copy_status": "not_needed" if project_type == "web" else "not_started",
        "materials_status": "not_started",
        "second_review": {"status": "not_started", "reviewer": None, "evidence": None},
        "preview": {
            "url": None,
            "entry_file": None,
            "production_root": None,
            "gpu_status": "not_verified",
        },
        "visual_approved": False,
        "audio": {"status": "not_requested", "provider": "doubao"},
        "next_questions": [],
        "change_notes": [],
    }
    sheet = io.StringIO(newline="")
    csv.writer(sheet).writerow(
        ["素材ID", "用途", "类型", "来源链接", "作者或来源", "原件相对路径",
         "筛选状态", "复核者", "复核记录", "备注"]
    )
    navigation = (
        f"# {name}：从这里开始\n\n"
        "先和助手确定方向、参考链接和大致效果，再按步骤找资料、做预览。\n\n"
        "- 核心分区：简报、定调、步骤与目标、素材台账和进度。\n"
        "- 素材库：原始材料与来源；过滤库：采用、存疑和未采用的记录。\n"
        "- 制作区：可修改源码或真实制作目录索引、预览与迭代记录。\n"
        "- 最终方案：用户确认的视觉版本；成品：交付入口及必要文件。\n\n"
        "视频先做静音网页视觉，不默认导出 MP4。视觉定稿后，声音单独交豆包。\n"
        "这些目录目前只是工作空间，初始化不代表素材复核或用户验收完成。\n"
    )
    brief = (
        f"# {name}：项目简报\n\n"
        "## 用户已经确定\n\n项目名：" + name + "\n\n"
        "## 本次建议\n\n由助手依据实际参考提出，再由用户选择。\n\n"
        "## 需要询问\n\n- 什么方向、给谁看？\n- 有什么参考链接或图片？\n"
        "- 希望大致做成什么样？\n\n用户回答后更新本文件，已有信息不重复索取。\n"
    )
    tone = (
        "# 定调方案\n\n方向尚未确认。\n\n"
        "## 实际参考与观察\n\n记录真正读到的内容；无法读取时说明缺口。\n\n"
        "## 用户的选择\n\n将已选的视觉特点与需要改变的地方写清楚。\n\n"
        "## 如何判断达到目标\n\n使用能观察到的布局、内容、色彩或节奏标准。\n"
    )
    plan = (
        "# 步骤与目标\n\n当前只完成项目初始化，下一步是思路问答。\n\n"
        "| 步骤 | 本步目标 | 所需输入 | 产出位置 | 完成依据 | 下一步 |\n"
        "|---|---|---|---|---|---|\n"
        "| 思路问答 | 确定方向、参考和预期样子 | 用户回答 | 项目简报与定调方案 | 用户选定方向 | 制订资料清单 |\n\n"
        "后续步骤按当前项目补充；视频推荐文案前置，网页可跳过声音分支。\n"
    )
    return {
        "00_核心分区/00_从这里开始.md": (navigation, "utf-8"),
        "00_核心分区/01_项目简报.md": (brief, "utf-8"),
        "00_核心分区/02_定调方案.md": (tone, "utf-8"),
        "00_核心分区/03_步骤与目标.md": (plan, "utf-8"),
        "00_核心分区/04_素材清单.csv": (sheet.getvalue(), "utf-8-sig"),
        "00_核心分区/进度.json": (json.dumps(progress, ensure_ascii=False, indent=2) + "\n", "utf-8"),
    }


def initialize(root: Path, name: str, project_type: str = "undecided") -> dict:
    name = name.strip()
    if not name:
        raise ValueError("项目名不能为空。")
    if project_type not in {"undecided", "web", "video"}:
        raise ValueError("项目类型必须为 undecided、web 或 video。")
    requested = Path(os.path.abspath(root.expanduser()))
    if _is_link(requested):
        raise ValueError("项目根目录是符号链接或联接目录，请选择独立目录。")
    if requested.exists() and not requested.is_dir():
        raise ValueError(f"项目根路径不是目录：{requested}")
    root = requested.resolve()
    files = _initial_files(name, project_type)
    # Check all conflicts before creating anything. Existing content is never replaced.
    for relative in DIRECTORIES:
        _validate_destination(root, relative, directory=True)
    for relative in files:
        _validate_destination(root, relative, directory=False)
    root.mkdir(parents=True, exist_ok=True)
    for relative in DIRECTORIES:
        (root / relative).mkdir(parents=True, exist_ok=True)
    created, preserved = [], []
    for relative, (body, encoding) in files.items():
        try:
            with (root / relative).open("x", encoding=encoding, newline="") as handle:
                handle.write(body)
            created.append(relative)
        except FileExistsError:
            preserved.append(relative)
    return {"ok": True, "root": str(root), "created_files": created, "preserved_files": preserved}


def main() -> int:
    parser = argparse.ArgumentParser(description="建立设计项目六个分区，已有文件和进度原样保留。")
    parser.add_argument("--root", type=Path, required=True, help="独立项目目录")
    parser.add_argument("--name", required=True, help="项目名称")
    parser.add_argument("--type", choices=["undecided", "web", "video"], default="undecided")
    args = parser.parse_args()
    try:
        result = initialize(args.root, args.name, args.type)
    except (OSError, ValueError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
