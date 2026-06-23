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


def str_to_hex(text: str, sep: str = " ", encoding: str = "utf-8") -> str:
    """字符串转十六进制字符串"""
    return bytes_to_hex(text.encode(encoding), sep=sep)


def hex_to_str(hex_str: str, encoding: str = "utf-8") -> str:
    """十六进制字符串转字符串，如 '41 42' -> 'AB'"""
    data = hex_to_bytes(hex_str)
    return data.decode(encoding, errors="replace")


def hex_to_bytes(hex_str: str) -> bytes:
    """十六进制字符串转字节，支持空格、逗号、0x 前缀"""
    cleaned = hex_str.replace(" ", "").replace(",", "").replace("0x", "").strip()
    if not cleaned:
        return b""
    if len(cleaned) % 2 != 0:
        cleaned = "0" + cleaned
    return bytes.fromhex(cleaned)


def is_valid_hex(hex_str: str) -> bool:
    """检查字符串是否为合法十六进制格式"""
    cleaned = hex_str.replace(" ", "").replace(",", "").strip()
    if not cleaned:
        return True
    try:
        bytes.fromhex(cleaned)
        return True
    except ValueError:
        return False
