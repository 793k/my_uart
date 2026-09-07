"""
tool_log.py — A5 5A A5 tool_log 帧流增量解码器

帧格式：MAGIC A5 5A A5 (3B) + type (1B) + payload_len (2B 大端) + payload
  type=1 POINT: payload 4B = flag(2B 大端) + value(2B 大端)，flag 名来自 point_codes.yaml
  type=2 TEXT:  UTF-8 日志文本，按行拆分
  type=3 RAW:   原样透传
  其它:         UNKNOWN

自 D:\yichip\demo\we_sdk\wearable-sdk\tools\serial-debug\serial_decoder.py
(FrameDecoder) 与 tools\sdk-log-parser\sdk_log_parser.py (MAGIC) 迁移，
解码行为与 SDK 工具保持一致。点码名映射不内置，一律由外部 YAML 提供。
"""

from __future__ import annotations

import time
from typing import Final, Optional

MAGIC: Final = b"\xA5\x5A\xA5"

FRAME_HEADER_SIZE = 6
MAX_PAYLOAD_LENGTH: Final = 240
INCOMPLETE_FRAME_TIMEOUT_S: Final = 1.0


class ToolLogDecoder:
    """增量解码 A5 5A A5 tool_log 帧流，未完整帧保留等待后续字节。

    feed(chunk) 返回本段字节对应的可读行（每行不含换行符）：完整帧解码为
    POINT/TEXT/RAW/UNKNOWN 行；帧外非帧字节不隐藏，转为可见文本行输出。
    帧边界丢失时自动重同步，保证后续帧不错位。
    """

    def __init__(
        self,
        *,
        point_codes: Optional[dict[int, str]] = None,
        incomplete_frame_timeout_s: float = INCOMPLETE_FRAME_TIMEOUT_S,
    ) -> None:
        self.buffer = bytearray()
        self.point_codes = dict(point_codes) if point_codes else {}
        self.incomplete_frame_timeout_s = incomplete_frame_timeout_s
        self.wait_started_at: float | None = None
        self.frames_decoded = 0
        self.resync_bytes = 0

    def feed(self, chunk: bytes) -> list[str]:
        """返回 chunk 中完整帧对应的可读输出行。

        帧与帧之间的非帧字节不隐藏：一律转为可见行返回（可打印文本
        原样、不可打印字节转义为 \\xNN），保证任何收到的字节都有显示。
        """
        lines: list[str] = []
        self.buffer.extend(chunk)
        while len(self.buffer) >= len(MAGIC):
            magic_index = self.buffer.find(MAGIC)
            if magic_index < 0:
                discard_count = len(self.buffer) - len(MAGIC) + 1
                lines.extend(self._garbage_lines(bytes(self.buffer[:discard_count])))
                self._resync(discard_count)
                del self.buffer[:discard_count]
                self.wait_started_at = None
                break
            if magic_index > 0:
                lines.extend(self._garbage_lines(bytes(self.buffer[:magic_index])))
                self._resync(magic_index)
                del self.buffer[:magic_index]
                self.wait_started_at = None
            if len(self.buffer) < FRAME_HEADER_SIZE:
                break
            frame_type = self.buffer[3]
            payload_length = (self.buffer[4] << 8) | self.buffer[5]
            frame_end = FRAME_HEADER_SIZE + payload_length
            if payload_length > MAX_PAYLOAD_LENGTH:
                lines.extend(self._garbage_lines(bytes(self.buffer[:1])))
                self._resync(1)
                del self.buffer[0]
                self.wait_started_at = None
                continue
            if len(self.buffer) < frame_end:
                if self.wait_started_at is None:
                    self.wait_started_at = time.monotonic()
                elif time.monotonic() - self.wait_started_at >= self.incomplete_frame_timeout_s:
                    # 半帧滞留超时，判定为噪声，丢弃头部字节继续重同步
                    lines.extend(self._garbage_lines(bytes(self.buffer[:1])))
                    self._resync(1)
                    del self.buffer[0]
                    self.wait_started_at = None
                    continue
                break
            payload = bytes(self.buffer[FRAME_HEADER_SIZE:frame_end])
            del self.buffer[:frame_end]
            self.wait_started_at = None
            self.frames_decoded += 1
            match frame_type:
                case 1:
                    lines.append(self._point(payload))
                case 2:
                    lines.extend(self._text(payload))
                case 3:
                    lines.append(f"[RAW] {payload_length}B: {payload[:16].hex(' ')}")
                case _:
                    lines.append(f"[UNKNOWN] type=0x{frame_type:02X} {payload_length} bytes")
        return lines

    @staticmethod
    def _garbage_lines(data: bytes) -> list[str]:
        """重同步丢弃的字节转为可见文本行（不可打印字节转义 \\xNN）。

        按换行拆行，可打印 ASCII/制表符原样保留；其余字节以 \\xNN 转义，
        只转换不丢弃，保证原始字节内容完整可见。
        """
        if not data:
            return []
        raw_parts = data.split(b"\n")
        if data.endswith(b"\n") and raw_parts and raw_parts[-1] == b"":
            raw_parts.pop()  # 末尾换行符本身不产生空行
        lines = []
        for raw_line in raw_parts:
            raw_line = raw_line.rstrip(b"\r")
            text = "".join(
                chr(c) if 32 <= c <= 126 or c in (9,) else f"\\x{c:02X}"
                for c in raw_line
            )
            lines.append(text)
        return lines

    def _resync(self, byte_count: int) -> None:
        """记录为对齐帧边界而丢弃的字节数。"""
        self.resync_bytes += byte_count

    def _point(self, payload: bytes) -> str:
        """渲染一条 type=1 点码帧。"""
        if len(payload) != 4:
            return f"[POINT] malformed payload: {len(payload)} bytes"
        flag = (payload[0] << 8) | payload[1]
        value = (payload[2] << 8) | payload[3]
        name = self.point_codes.get(flag, f"UNKNOWN({flag:04X})")
        return f"[POINT] {name} value={value}"

    @staticmethod
    def _text(payload: bytes) -> list[str]:
        """按行拆分 type=2 文本帧内容。"""
        return payload.decode("utf-8", errors="replace").splitlines() or [""]


def load_point_codes(path: str) -> dict[int, str]:
    """读取 YAML 点码表，返回 flag → 名称 映射（唯一事实源，无内置表）。

    YAML 内容为 ``flag: 名称`` 映射，flag 支持 0x0100 / "0x0100" 引号串 / 十进制：
      "0x0130": SYS_LOG_POINT_NEW_FEATURE
    文件缺失或损坏时由调用方降级（保持当前表）。
    """
    import yaml

    codes: dict[int, str] = {}
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if data is None:  # 空文件/纯注释
        return codes
    if not isinstance(data, dict):
        raise ValueError("点码表应为 flag: 名称 映射结构")
    for key, name in data.items():
        if isinstance(key, int):
            flag = key
        elif isinstance(key, str):
            text = key.strip()
            flag = int(text, 16) if text.lower().startswith("0x") else int(text)
        else:
            raise ValueError(f"点码键格式不支持: {key!r}")
        codes[flag] = str(name)
    return codes
