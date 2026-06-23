"""
serial_core.py — 串口核心逻辑（无 UI 依赖，可单独测试）
"""

import serial
import serial.tools.list_ports
import threading
import time
from typing import Callable, Optional, List


class SerialCore:
    """串口核心类：封装所有串口操作，线程安全"""

    def __init__(self):
        self._ser: Optional[serial.Serial] = None
        self._port_name: str = ""
        self._running = False
        self._rx_thread: Optional[threading.Thread] = None
        self._callback: Optional[Callable[[bytes], None]] = None
        self._lock = threading.Lock()
        self._last_error: str = ""

    def list_ports(self) -> List[dict]:
        """扫描可用串口，返回端口信息列表，每项包含 device 和 description"""
        return [
            {"device": p.device, "description": p.description or "未知设备"}
            for p in serial.tools.list_ports.comports()
        ]

    def open(self, port: str, baud: int, data_bits: int,
             stop_bits: float, parity: str) -> bool:
        """打开串口，返回是否成功"""
        parity_map = {
            "None": serial.PARITY_NONE,
            "Even": serial.PARITY_EVEN,
            "Odd": serial.PARITY_ODD,
            "Mark": serial.PARITY_MARK,
            "Space": serial.PARITY_SPACE,
        }
        stop_map = {
            1: serial.STOPBITS_ONE,
            1.5: serial.STOPBITS_ONE_POINT_FIVE,
            2: serial.STOPBITS_TWO,
        }
        bytesize_map = {
            5: serial.FIVEBITS,
            6: serial.SIXBITS,
            7: serial.SEVENBITS,
            8: serial.EIGHTBITS,
        }

        try:
            self._ser = serial.Serial(
                port=port,
                baudrate=baud,
                bytesize=bytesize_map.get(data_bits, serial.EIGHTBITS),
                parity=parity_map.get(parity, serial.PARITY_NONE),
                stopbits=stop_map.get(stop_bits, serial.STOPBITS_ONE),
                timeout=0.1,
                write_timeout=1.0,
            )
            self._port_name = port
            self._running = True
            self._rx_thread = threading.Thread(target=self._rx_loop, daemon=True)
            self._rx_thread.start()
            self._last_error = ""
            return True
        except Exception as e:
            self._last_error = str(e)
            return False

    def close(self) -> None:
        """关闭串口"""
        self._running = False
        if self._rx_thread and self._rx_thread.is_alive():
            self._rx_thread.join(timeout=1.0)
        if self._ser and self._ser.is_open:
            self._ser.close()
        self._ser = None
        self._port_name = ""

    def is_open(self) -> bool:
        """串口是否已打开"""
        return self._ser is not None and self._ser.is_open

    def send(self, data: bytes) -> bool:
        """发送原始字节，返回是否成功"""
        if not self.is_open():
            return False
        try:
            with self._lock:
                self._ser.write(data)
            return True
        except Exception as e:
            self._last_error = str(e)
            return False

    def send_string(self, text: str, encoding: str = "utf-8") -> bool:
        """发送字符串"""
        try:
            return self.send(text.encode(encoding))
        except Exception as e:
            self._last_error = str(e)
            return False

    def send_hex(self, hex_str: str) -> bool:
        """发送十六进制字符串，如 '01 02 AB'"""
        try:
            cleaned = hex_str.replace(" ", "").replace(",", "").strip()
            if len(cleaned) % 2 != 0:
                cleaned = "0" + cleaned
            data = bytes.fromhex(cleaned)
            return self.send(data)
        except Exception as e:
            self._last_error = f"HEX 格式错误: {e}"
            return False

    def set_rx_callback(self, callback: Callable[[bytes], None]) -> None:
        """设置接收数据回调"""
        self._callback = callback

    def get_last_error(self) -> str:
        """获取最后一次错误信息"""
        return self._last_error

    def _rx_loop(self) -> None:
        """后台接收线程"""
        while self._running and self._ser and self._ser.is_open:
            try:
                in_waiting = self._ser.in_waiting
                if in_waiting > 0:
                    data = self._ser.read(in_waiting)
                    if data and self._callback:
                        self._callback(data)
                else:
                    time.sleep(0.005)
            except Exception:
                break

    def get_port_info(self) -> str:
        """获取当前串口信息"""
        if self.is_open():
            return f"{self._port_name} @ {self._ser.baudrate}"
        return ""

    def update_params(self, baud: int, data_bits: int,
                      stop_bits: float, parity: str) -> bool:
        """串口打开状态下实时更新参数"""
        if not self.is_open():
            return False

        parity_map = {
            "None": serial.PARITY_NONE,
            "Even": serial.PARITY_EVEN,
            "Odd": serial.PARITY_ODD,
            "Mark": serial.PARITY_MARK,
            "Space": serial.PARITY_SPACE,
        }
        stop_map = {
            1: serial.STOPBITS_ONE,
            1.5: serial.STOPBITS_ONE_POINT_FIVE,
            2: serial.STOPBITS_TWO,
        }
        bytesize_map = {
            5: serial.FIVEBITS,
            6: serial.SIXBITS,
            7: serial.SEVENBITS,
            8: serial.EIGHTBITS,
        }

        try:
            with self._lock:
                self._ser.baudrate = baud
                self._ser.bytesize = bytesize_map.get(data_bits, serial.EIGHTBITS)
                self._ser.parity = parity_map.get(parity, serial.PARITY_NONE)
                self._ser.stopbits = stop_map.get(stop_bits, serial.STOPBITS_ONE)
            self._last_error = ""
            return True
        except Exception as e:
            self._last_error = str(e)
            return False
