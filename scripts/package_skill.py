#!/usr/bin/env python3
"""Build a small, self-contained Agent Skill zip from the repository."""

from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
INCLUDE = (
    Path("SKILL.md"),
    Path("assets/trip.example.json"),
    Path("assets/readme-day-card.svg"),
    Path("web/README.md"),
)
DIRECTORIES = (Path("scripts"), Path("references"), Path("bridge"))


def package(output: Path) -> list[str]:
    files = list(INCLUDE)
    for directory in DIRECTORIES:
        files.extend(path.relative_to(ROOT) for path in (ROOT / directory).rglob("*") if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc")
    output = output.resolve()
    if output.is_relative_to(ROOT):
        raise ValueError("请将压缩包输出到仓库外，避免误将发布产物打入自身")
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for relative in sorted(set(files)):
            archive.write(ROOT / relative, relative.as_posix())
    return [relative.as_posix() for relative in sorted(set(files))]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="仓库外的 ZIP 路径")
    args = parser.parse_args()
    files = package(args.output)
    print(f"已打包 {len(files)} 个文件：{args.output.resolve()}")


if __name__ == "__main__":
    main()
