"""
utils.py — 工具函数
"""


def bytes_to_hex(data: bytes, sep: str = " ") -> str:
    """字节转十六进制字符串，如 b'\\x01\\x41' -> '01 41'"""
    return sep.join(f"{b:02X}" for b in data)


def bytes_to_ascii(data: bytes) -> str:
    """字节转 ASCII 字符串，不可见字符显示为 '.'"""
    return "".join(chr(b) if 32 <= b <= 126 else "." for b in data)


def format_rx_data(data: bytes, hex_mode: bool) -> str:
    """按模式格式化接收到的数据"""
    if hex_mode:
        return bytes_to_hex(data) + " "
    try:
        return data.decode("utf-8", errors="replace")
    except Exception:
        return bytes_to_ascii(data)
