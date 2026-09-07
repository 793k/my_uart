"""
app_cache.py — 本地缓存目录管理（位于系统"文档"目录，集中统一）

目录：<文档>/UART_Helper/
  README.txt        说明文档（标注本程序生成，可安全删除）
  .settings.json    界面参数缓存（原保存在 exe/源码旁，现迁移至此）
  point_codes.yaml  点码表缓存（由 UI「点码表」选择的 yaml 复制而来，
                    也是 A5 帧解析启动时读取的唯一来源）
  rx_backup/        接收缓冲区超限时的自动备份数据

可通过环境变量 UART_HELPER_CACHE_DIR 覆盖根目录（测试/便携场景）。
"""

import os
import shutil
from typing import Optional

from config import CACHE_FOLDER_NAME, RX_BACKUP_DIR

DOC_TEXT = """UART 串口助手 — 本地缓存目录
====================================
本目录由「UART 串口助手」(793k的串口助手x.exe) 自动生成与管理，
用于存放该程序的本地缓存数据。删除本目录不影响程序本体，
程序会在下次运行时自动重新创建。

文件说明：
- README.txt          本说明文件
- .settings.json      界面参数缓存（串口、波特率、显示开关等）
- point_codes.yaml    点码名映射表缓存：由程序内「点码表」按钮选择的
                      YAML 配置文件复制而来；A5 帧解析勾选时加载此缓存，
                      也可直接用文本编辑器修改后重开一次解析开关生效
- rx_backup/          接收缓冲区超限时自动备份的原始接收数据

不再使用本程序时，可放心删除整个目录。
"""


def get_cache_dir() -> str:
    """返回并确保缓存目录存在。"""
    env_override = os.environ.get("UART_HELPER_CACHE_DIR")
    if env_override:
        base_dir = env_override
    else:
        from PyQt6.QtCore import QStandardPaths
        base_dir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation
        )
        if not base_dir:
            base_dir = os.path.expanduser("~")
    cache_dir = os.path.join(base_dir, CACHE_FOLDER_NAME)
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def ensure_docs() -> str:
    """确保缓存目录内存在说明文档，返回缓存目录路径。"""
    cache_dir = get_cache_dir()
    doc_path = os.path.join(cache_dir, "README.txt")
    if not os.path.exists(doc_path):
        try:
            with open(doc_path, "w", encoding="utf-8") as f:
                f.write(DOC_TEXT)
        except OSError:
            pass
    return cache_dir


def rx_backup_dir() -> str:
    """返回接收数据自动备份目录（缓存目录内）。"""
    backup_dir = os.path.join(get_cache_dir(), RX_BACKUP_DIR)
    os.makedirs(backup_dir, exist_ok=True)
    return backup_dir


def _legacy_app_file(name: str) -> str:
    """旧版缓存路径：打包后 exe 所在目录；开发时源码所在目录。"""
    import sys
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, name)


# ===== 设置文件 =====

def settings_path() -> str:
    """返回设置文件路径：缓存内；旧位置文件存在则迁移一次（copy，不删原文件）。"""
    cache_file = os.path.join(get_cache_dir(), ".settings.json")
    if not os.path.exists(cache_file):
        legacy = _legacy_app_file(".settings.json")
        if os.path.exists(legacy):
            try:
                shutil.copy2(legacy, cache_file)
            except OSError:
                pass
    return cache_file


# ===== 点码表 =====

def point_codes_cache_path() -> str:
    """返回点码表缓存路径。"""
    return os.path.join(get_cache_dir(), "point_codes.yaml")


def resolve_point_codes_file() -> Optional[str]:
    """返回要读取的点码表路径：仅文档目录缓存；未配置时返回 None。

    用户通过「选择 YAML 点码表」按钮把所选文件复制为缓存后此处才有值。
    """
    cache_file = point_codes_cache_path()
    if os.path.exists(cache_file):
        return cache_file
    return None


def cache_point_codes_from(source: str) -> str:
    """把用户选择的 YAML 点码表复制到缓存，返回缓存路径（覆盖旧缓存）。"""
    cache_file = point_codes_cache_path()
    shutil.copy2(source, cache_file)
    return cache_file
