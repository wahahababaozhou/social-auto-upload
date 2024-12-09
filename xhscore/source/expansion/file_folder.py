from contextlib import suppress
from pathlib import Path
import os


def file_switch(path: Path) -> None:
    """切换文件的存在性，如果文件存在则删除，否则创建"""
    if path.exists():
        path.unlink()
    else:
        path.touch()


def remove_empty_directories(path: Path) -> None:
    """删除空目录，排除特定目录"""
    exclude = {
        "\\.",  # 排除以"."开头的目录
        "\\_",  # 排除以"_"开头的目录
        "\\__", # 排除以"__"开头的目录
    }

    # 使用os.walk来递归遍历目录
    for dir_path, dir_names, file_names in os.walk(path, topdown=False):
        # 转换 dir_path 为 Path 对象
        dir_path = Path(dir_path)

        # 跳过匹配到的排除目录
        if any(exclude_str in str(dir_path) for exclude_str in exclude):
            continue

        # 如果目录为空，删除
        if not dir_names and not file_names:
            with suppress(OSError):
                dir_path.rmdir()
                print(f"Deleted empty directory: {dir_path}")
