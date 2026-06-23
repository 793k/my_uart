"""
ui_main.py — 主窗口界面（PyQt6）美化版
"""

import json
import os
import sys
import time
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QComboBox, QPushButton, QLineEdit, QTextEdit,
    QLabel, QCheckBox, QSpinBox, QMessageBox, QFileDialog, QFrame,
    QSizePolicy, QSplitter
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize, QRect
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon, QPainter, QPen, QBrush, QPixmap, QTextOption

from config import (
    BAUD_RATES, DATA_BITS, STOP_BITS, PARITY_OPTIONS,
    DEFAULT_BAUD, DEFAULT_DATA_BITS, DEFAULT_STOP_BITS, DEFAULT_PARITY,
    TIMER_INTERVALS, DEFAULT_TIMER_INTERVAL,
    RX_BUFFER_OPTIONS, DEFAULT_RX_BUFFER, RX_BACKUP_DIR,
    TIMESTAMP_TIMEOUT_OPTIONS, DEFAULT_TIMESTAMP_TIMEOUT,
    FRAME_GAP_OPTIONS, DEFAULT_FRAME_GAP,
    DEFAULT_FONT_SIZE, DEFAULT_LINE_SPACING,
    WINDOW_TITLE, WINDOW_MIN_SIZE,
    STATUS_CONNECTED, STATUS_DISCONNECTED, STATUS_ERROR,
)
from serial_core import SerialCore
from utils import format_rx_data, str_to_hex, hex_to_str, is_valid_hex


# ============ 全局 QSS 样式 ============
APP_STYLE = """
QMainWindow {
    background-color: #f0f2f5;
}

QGroupBox {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 8px;
    font-weight: 600;
    font-size: 13px;
    color: #333333;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 6px;
    color: #2196F3;
}

QPushButton {
    background-color: #2196F3;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 7px 16px;
    font-size: 13px;
    font-weight: 500;
    min-height: 28px;
}

QPushButton:hover {
    background-color: #1976D2;
}

QPushButton:pressed {
    background-color: #0D47A1;
}

QPushButton:disabled {
    background-color: #b0bec5;
    color: #eceff1;
}

QPushButton#secondary {
    background-color: #607d8b;
}

QPushButton#secondary:hover {
    background-color: #455a64;
}

QPushButton#danger {
    background-color: #ef5350;
}

QPushButton#danger:hover {
    background-color: #d32f2f;
}

QPushButton#success {
    background-color: #66bb6a;
}

QPushButton#success:hover {
    background-color: #43a047;
}

QComboBox {
    background-color: #ffffff;
    border: 1px solid #c0c0c0;
    border-radius: 6px;
    padding: 4px 10px;
    min-height: 28px;
    font-size: 13px;
    color: #333333;
}

QComboBox:hover {
    border: 1px solid #90caf9;
    background-color: #f5f9ff;
}

QComboBox:focus {
    border: 1px solid #2196F3;
    background-color: #ffffff;
}

QComboBox::drop-down {
    border: none;
    width: 26px;
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #78909c;
    width: 0px;
    height: 0px;
}

QComboBox::down-arrow:on {
    border-top: none;
    border-bottom: 6px solid #2196F3;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #c0c0c0;
    border-radius: 6px;
    selection-background-color: #e3f2fd;
    selection-color: #1565C0;
    padding: 4px;
    outline: none;
}

QComboBox QAbstractItemView::item {
    min-height: 26px;
    padding: 4px 8px;
    border-radius: 4px;
}

QComboBox QAbstractItemView::item:hover {
    background-color: #e3f2fd;
    color: #1565C0;
}

QComboBox QAbstractItemView::item:selected {
    background-color: #bbdefb;
    color: #0d47a1;
}

QLineEdit {
    background-color: #ffffff;
    border: 1px solid #c0c0c0;
    border-radius: 5px;
    padding: 5px 8px;
    min-height: 24px;
    font-size: 13px;
    color: #333333;
}

QLineEdit:focus {
    border: 1px solid #2196F3;
}

QTextEdit {
    background-color: #fafafa;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 8px;
    color: #333333;
    selection-background-color: #bbdefb;
}

QTextEdit:focus {
    border: 1px solid #2196F3;
}

QLabel {
    font-size: 13px;
    color: #555555;
}

QLabel#title {
    font-size: 16px;
    font-weight: 700;
    color: #1565C0;
}

QLabel#status {
    font-size: 13px;
    font-weight: 600;
}

QCheckBox {
    font-size: 13px;
    color: #555555;
    spacing: 6px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 3px;
    border: 1px solid #c0c0c0;
    background-color: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #2196F3;
    border: 1px solid #2196F3;
}

QSplitter::handle {
    background-color: #d0d0d0;
    width: 2px;
}

QSplitter::handle:hover {
    background-color: #2196F3;
}
"""


class MainWindow(QMainWindow):
    """串口助手主窗口 — 美化版"""

    sig_rx_data = pyqtSignal(bytes)
    sig_status = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.serial = SerialCore()
        self.rx_buffer = ""
        self.rx_count = 0
        self.tx_count = 0
        self.hex_rx = False
        self.hex_tx = False
        self.max_rx_buffer = DEFAULT_RX_BUFFER
        self.timestamp_enabled = False
        self.timestamp_timeout = DEFAULT_TIMESTAMP_TIMEOUT
        self.frame_gap_enabled = False
        self.frame_gap_ms = DEFAULT_FRAME_GAP
        self._last_rx_time = 0.0
        self._backup_counter = 0
        self._raw_rx_bytes = bytearray()
        self.timer_send = QTimer(self)
        self.timer_send.timeout.connect(self.on_send_clicked)
        self._display_font_size = DEFAULT_FONT_SIZE
        self._display_line_spacing = DEFAULT_LINE_SPACING

        self._build_ui()
        self._connect_signals()
        self._refresh_ports()
        self._load_settings()
        self._apply_status(STATUS_DISCONNECTED)

    def _build_ui(self):
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(*WINDOW_MIN_SIZE)
        self.setStyleSheet(APP_STYLE)

        mono_font = QFont("Consolas", 11)
        title_font = QFont("Microsoft YaHei", 10)

        central = QWidget()
        self.setCentralWidget(central)
        outer_v = QVBoxLayout(central)
        outer_v.setContentsMargins(16, 16, 16, 16)
        outer_v.setSpacing(14)

        # ===== 顶部标题栏 =====
        title_h = QHBoxLayout()
        self.lbl_title = QLabel("UART 串口助手")
        self.lbl_title.setObjectName("title")
        self.lbl_title.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        title_h.addWidget(self.lbl_title)
        title_h.addStretch()
        outer_v.addLayout(title_h)

        # ===== 主内容区（三栏） =====
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ---- 左侧面板：串口设置 ----
        left_widget = QWidget()
        left_widget.setMaximumWidth(280)
        left_panel = QVBoxLayout(left_widget)
        left_panel.setContentsMargins(0, 0, 0, 0)
        left_panel.setSpacing(12)

        grp_settings = QGroupBox("串口设置")
        v = QVBoxLayout(grp_settings)
        v.setSpacing(10)
        v.setContentsMargins(14, 16, 14, 14)

        # 串口号（下拉框 + 刷新按钮同行）
        v.addWidget(QLabel("串口号"))
        h_port = QHBoxLayout()
        h_port.setSpacing(6)
        self.cmb_port = QComboBox()
        self.cmb_port.setMinimumWidth(160)
        self.cmb_port.setMinimumContentsLength(20)
        self.cmb_port.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.cmb_port.setMinimumHeight(32)
        h_port.addWidget(self.cmb_port, 1)
        self.btn_refresh = QPushButton("\u27F3")
        self.btn_refresh.setObjectName("secondary")
        self.btn_refresh.setFixedSize(32, 32)
        self.btn_refresh.setToolTip("刷新端口列表")
        self.btn_refresh.setStyleSheet("QPushButton { border-radius: 16px; font-size: 14px; padding: 0px; }")
        h_port.addWidget(self.btn_refresh)
        v.addLayout(h_port)

        # 波特率
        v.addWidget(QLabel("波特率"))
        self.cmb_baud = QComboBox()
        self.cmb_baud.addItems(map(str, BAUD_RATES))
        self.cmb_baud.setCurrentText(str(DEFAULT_BAUD))
        self.cmb_baud.setEditable(True)
        v.addWidget(self.cmb_baud)

        # 数据位 / 停止位 同行
        h_bits = QHBoxLayout()
        h_bits.addWidget(QLabel("数据位"))
        self.cmb_data = QComboBox()
        self.cmb_data.addItems(map(str, DATA_BITS))
        self.cmb_data.setCurrentText(str(DEFAULT_DATA_BITS))
        h_bits.addWidget(self.cmb_data, 1)
        h_bits.addSpacing(10)
        h_bits.addWidget(QLabel("停止位"))
        self.cmb_stop = QComboBox()
        self.cmb_stop.addItems(map(str, STOP_BITS))
        self.cmb_stop.setCurrentText(str(DEFAULT_STOP_BITS))
        h_bits.addWidget(self.cmb_stop, 1)
        v.addLayout(h_bits)

        # 校验位
        v.addWidget(QLabel("校验位"))
        self.cmb_parity = QComboBox()
        self.cmb_parity.addItems(PARITY_OPTIONS)
        self.cmb_parity.setCurrentText(DEFAULT_PARITY)
        v.addWidget(self.cmb_parity)

        # 接收缓冲区大小
        v.addWidget(QLabel("接收缓冲区 (字节)"))
        self.cmb_buffer = QComboBox()
        self.cmb_buffer.addItems([f"{x:,}" for x in RX_BUFFER_OPTIONS])
        self.cmb_buffer.setCurrentText(f"{DEFAULT_RX_BUFFER:,}")
        self.cmb_buffer.setEditable(True)
        self.cmb_buffer.currentTextChanged.connect(self.on_buffer_changed)
        v.addWidget(self.cmb_buffer)

        # 打开/关闭按钮
        self.btn_open = QPushButton("打开串口")
        self.btn_open.setMinimumHeight(38)
        v.addWidget(self.btn_open)

        # 状态指示灯
        h_status = QHBoxLayout()
        self.lbl_status_dot = QLabel("●")
        self.lbl_status_dot.setFont(QFont("Arial", 16))
        self.lbl_status_dot.setStyleSheet("color: #9e9e9e;")
        h_status.addWidget(self.lbl_status_dot)
        self.lbl_status = QLabel(STATUS_DISCONNECTED)
        self.lbl_status.setObjectName("status")
        h_status.addWidget(self.lbl_status)
        h_status.addStretch()
        v.addLayout(h_status)

        v.addStretch()
        left_panel.addWidget(grp_settings)
        left_panel.addStretch()
        splitter.addWidget(left_widget)

        # ---- 中间面板：接收区 + 发送记录 ----
        mid_widget = QWidget()
        mid_panel = QVBoxLayout(mid_widget)
        mid_panel.setContentsMargins(0, 0, 0, 0)
        mid_panel.setSpacing(10)

        mid_splitter = QSplitter(Qt.Orientation.Vertical)

        # 接收区
        grp_rx = QGroupBox("接收数据")
        v2 = QVBoxLayout(grp_rx)
        v2.setSpacing(8)
        v2.setContentsMargins(14, 16, 14, 14)

        self.txt_rx = QTextEdit()
        self.txt_rx.setFont(mono_font)
        self.txt_rx.setReadOnly(True)
        self.txt_rx.setPlaceholderText("接收到的数据将显示在这里...")
        v2.addWidget(self.txt_rx)

        # 接收区工具栏 - 第一行：功能开关
        h_rx1 = QHBoxLayout()
        h_rx1.setSpacing(10)
        self.chk_hex_rx = QCheckBox("HEX")
        self.chk_hex_rx.setToolTip("HEX 显示模式")
        self.chk_hex_rx.stateChanged.connect(self.on_hex_rx_changed)
        h_rx1.addWidget(self.chk_hex_rx)
        self.chk_timestamp = QCheckBox("时间戳")
        self.chk_timestamp.stateChanged.connect(self.on_timestamp_changed)
        h_rx1.addWidget(self.chk_timestamp)
        self.chk_pause_rx = QCheckBox("暂停")
        self.chk_pause_rx.setToolTip("暂停接收")
        h_rx1.addWidget(self.chk_pause_rx)
        h_rx1.addSpacing(10)
        self.chk_show_tx_log = QCheckBox("发送记录")
        self.chk_show_tx_log.setToolTip("显示/隐藏发送记录窗口")
        self.chk_show_tx_log.setChecked(True)
        self.chk_show_tx_log.stateChanged.connect(self.on_show_tx_log_changed)
        h_rx1.addWidget(self.chk_show_tx_log)
        h_rx1.addStretch()
        v2.addLayout(h_rx1)

        # 接收区工具栏 - 第二行：超时/帧间隔 + 操作按钮
        h_rx2 = QHBoxLayout()
        h_rx2.setSpacing(10)
        self.chk_timeout = QCheckBox("超时")
        self.chk_timeout.setToolTip("超时标记")
        self.chk_timeout.stateChanged.connect(self.on_timeout_changed)
        h_rx2.addWidget(self.chk_timeout)
        h_rx2.addWidget(QLabel("ms:"))
        self.cmb_timeout = QComboBox()
        self.cmb_timeout.addItems(map(str, TIMESTAMP_TIMEOUT_OPTIONS))
        self.cmb_timeout.setCurrentText(str(DEFAULT_TIMESTAMP_TIMEOUT))
        self.cmb_timeout.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.cmb_timeout.currentTextChanged.connect(self.on_timeout_interval_changed)
        h_rx2.addWidget(self.cmb_timeout)
        h_rx2.addSpacing(10)

        self.chk_frame_gap = QCheckBox("帧间隔")
        self.chk_frame_gap.setToolTip("基于字节间隔智能分组：同一帧内仅显示一次时间戳")
        self.chk_frame_gap.stateChanged.connect(self.on_frame_gap_changed)
        h_rx2.addWidget(self.chk_frame_gap)
        h_rx2.addWidget(QLabel("ms:"))
        self.cmb_frame_gap = QComboBox()
        self.cmb_frame_gap.addItems(map(str, FRAME_GAP_OPTIONS))
        self.cmb_frame_gap.setCurrentText(str(DEFAULT_FRAME_GAP))
        self.cmb_frame_gap.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.cmb_frame_gap.currentTextChanged.connect(self.on_frame_gap_interval_changed)
        h_rx2.addWidget(self.cmb_frame_gap)

        h_rx2.addStretch()
        self.btn_clear_rx = QPushButton("清空")
        self.btn_clear_rx.setObjectName("danger")
        h_rx2.addWidget(self.btn_clear_rx)
        self.btn_save_rx = QPushButton("保存")
        self.btn_save_rx.setObjectName("success")
        h_rx2.addWidget(self.btn_save_rx)
        v2.addLayout(h_rx2)

        mid_splitter.addWidget(grp_rx)

        # 发送记录区
        self.grp_tx_log = QGroupBox("发送记录")
        grp_tx_log = self.grp_tx_log
        v_tx_log = QVBoxLayout(grp_tx_log)
        v_tx_log.setSpacing(8)
        v_tx_log.setContentsMargins(14, 16, 14, 14)

        self.txt_tx_log = QTextEdit()
        self.txt_tx_log.setFont(mono_font)
        self.txt_tx_log.setReadOnly(True)
        self.txt_tx_log.setPlaceholderText("已发送的数据将显示在这里...")
        v_tx_log.addWidget(self.txt_tx_log)

        h_tx_log = QHBoxLayout()
        h_tx_log.setSpacing(10)
        self.chk_tx_log_timestamp = QCheckBox("时间戳")
        self.chk_tx_log_timestamp.setChecked(True)
        h_tx_log.addWidget(self.chk_tx_log_timestamp)
        h_tx_log.addStretch()
        self.btn_clear_tx_log = QPushButton("清空")
        self.btn_clear_tx_log.setObjectName("danger")
        h_tx_log.addWidget(self.btn_clear_tx_log)
        v_tx_log.addLayout(h_tx_log)

        mid_splitter.addWidget(self.grp_tx_log)
        mid_splitter.setStretchFactor(0, 3)
        mid_splitter.setStretchFactor(1, 1)

        mid_panel.addWidget(mid_splitter)

        # 统计信息
        h_stats = QHBoxLayout()
        h_stats.addStretch()
        self.lbl_stats = QLabel("RX: 0 bytes  |  TX: 0 bytes")
        self.lbl_stats.setStyleSheet("color: #888888; font-size: 12px;")
        h_stats.addWidget(self.lbl_stats)
        mid_panel.addLayout(h_stats)

        splitter.addWidget(mid_widget)

        # ---- 右侧面板：发送 + 工具 ----
        right_widget = QWidget()
        right_widget.setMaximumWidth(320)
        right_panel = QVBoxLayout(right_widget)
        right_panel.setContentsMargins(0, 0, 0, 0)
        right_panel.setSpacing(10)

        # 发送区
        grp_tx = QGroupBox("发送数据")
        v3 = QVBoxLayout(grp_tx)
        v3.setSpacing(8)
        v3.setContentsMargins(14, 16, 14, 14)

        self.txt_tx = QTextEdit()
        self.txt_tx.setFont(mono_font)
        self.txt_tx.setPlaceholderText("在此输入要发送的内容...")
        self.txt_tx.setMaximumHeight(120)
        v3.addWidget(self.txt_tx)

        h_tx = QHBoxLayout()
        self.chk_hex_tx = QCheckBox("HEX 发送")
        self.chk_hex_tx.stateChanged.connect(self.on_hex_tx_changed)
        h_tx.addWidget(self.chk_hex_tx)
        self.chk_newline = QCheckBox("追加 \\r\\n")
        h_tx.addWidget(self.chk_newline)
        h_tx.addStretch()
        self.btn_send = QPushButton("发送")
        self.btn_send.setObjectName("success")
        self.btn_send.setEnabled(False)
        h_tx.addWidget(self.btn_send)
        v3.addLayout(h_tx)
        right_panel.addWidget(grp_tx)

        # 定时发送
        grp_timer = QGroupBox("定时发送")
        v4 = QVBoxLayout(grp_timer)
        v4.setSpacing(8)
        v4.setContentsMargins(14, 16, 14, 14)

        h_timer = QHBoxLayout()
        self.chk_timer = QCheckBox("启用")
        self.chk_timer.toggled.connect(self.on_timer_toggled)
        h_timer.addWidget(self.chk_timer)
        h_timer.addWidget(QLabel("间隔 ms:"))
        self.cmb_interval = QComboBox()
        self.cmb_interval.addItems(map(str, TIMER_INTERVALS))
        self.cmb_interval.setCurrentText(str(DEFAULT_TIMER_INTERVAL))
        self.cmb_interval.setEditable(True)
        self.cmb_interval.setMaximumWidth(80)
        h_timer.addWidget(self.cmb_interval)
        h_timer.addStretch()
        v4.addLayout(h_timer)
        right_panel.addWidget(grp_timer)

        # 保存选项
        grp_save = QGroupBox("保存选项")
        v5 = QVBoxLayout(grp_save)
        v5.setSpacing(8)
        v5.setContentsMargins(14, 16, 14, 14)

        h_fmt = QHBoxLayout()
        h_fmt.addWidget(QLabel("格式"))
        self.cmb_save_fmt = QComboBox()
        self.cmb_save_fmt.addItems(["文本 (.txt)", "HEX (.txt)", "二进制 (.bin)"])
        h_fmt.addWidget(self.cmb_save_fmt, 1)
        v5.addLayout(h_fmt)

        h_path = QHBoxLayout()
        self.edt_save_path = QLineEdit()
        self.edt_save_path.setPlaceholderText("保存路径...")
        h_path.addWidget(self.edt_save_path)
        self.btn_browse = QPushButton("...")
        self.btn_browse.setFixedWidth(36)
        self.btn_browse.setObjectName("secondary")
        h_path.addWidget(self.btn_browse)
        v5.addLayout(h_path)

        self.btn_save = QPushButton("保存接收数据")
        v5.addWidget(self.btn_save)
        right_panel.addWidget(grp_save)

        # HEX 转换
        grp_hex = QGroupBox("HEX 转换")
        v6 = QVBoxLayout(grp_hex)
        v6.setSpacing(8)
        v6.setContentsMargins(14, 16, 14, 14)

        self.txt_hex_in = QTextEdit()
        self.txt_hex_in.setFont(mono_font)
        self.txt_hex_in.setPlaceholderText("输入内容...")
        self.txt_hex_in.setMaximumHeight(70)
        v6.addWidget(self.txt_hex_in)

        h_dir = QHBoxLayout()
        self.cmb_hex_dir = QComboBox()
        self.cmb_hex_dir.addItems(["字符串 → HEX", "HEX → 字符串"])
        h_dir.addWidget(self.cmb_hex_dir)
        h_dir.addStretch()
        self.btn_hex_convert = QPushButton("转换")
        self.btn_hex_convert.setObjectName("secondary")
        h_dir.addWidget(self.btn_hex_convert)
        v6.addLayout(h_dir)

        self.txt_hex_out = QTextEdit()
        self.txt_hex_out.setFont(mono_font)
        self.txt_hex_out.setReadOnly(True)
        self.txt_hex_out.setPlaceholderText("结果...")
        self.txt_hex_out.setMaximumHeight(70)
        v6.addWidget(self.txt_hex_out)
        right_panel.addWidget(grp_hex)

        # 显示设置
        grp_display = QGroupBox("显示设置")
        v7 = QVBoxLayout(grp_display)
        v7.setSpacing(8)
        v7.setContentsMargins(14, 16, 14, 14)

        h_size = QHBoxLayout()
        h_size.addWidget(QLabel("大小"))
        self.cmb_font_size = QComboBox()
        self.cmb_font_size.addItems(map(str, range(8, 21)))
        self.cmb_font_size.setCurrentText(str(DEFAULT_FONT_SIZE))
        self.cmb_font_size.setEditable(True)
        self.cmb_font_size.setMaximumWidth(60)
        self.cmb_font_size.currentTextChanged.connect(self.on_display_setting_changed)
        h_size.addWidget(self.cmb_font_size)
        h_size.addStretch()
        v7.addLayout(h_size)

        h_line = QHBoxLayout()
        h_line.addWidget(QLabel("行距"))
        self.cmb_line_spacing = QComboBox()
        self.cmb_line_spacing.addItems(["1.0", "1.2", "1.5", "1.8", "2.0"])
        self.cmb_line_spacing.setCurrentText(str(DEFAULT_LINE_SPACING))
        self.cmb_line_spacing.setMaximumWidth(60)
        self.cmb_line_spacing.currentTextChanged.connect(self.on_display_setting_changed)
        h_line.addWidget(self.cmb_line_spacing)
        h_line.addStretch()
        v7.addLayout(h_line)

        right_panel.addWidget(grp_display)

        right_panel.addStretch()
        splitter.addWidget(right_widget)

        # 设置分割器初始比例
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        outer_v.addWidget(splitter, 1)

        self._apply_display_settings()

    def _apply_display_settings(self):
        """应用字号和行间距到接收区和发送记录区"""
        try:
            size = int(self.cmb_font_size.currentText())
        except ValueError:
            size = DEFAULT_FONT_SIZE
        try:
            spacing = float(self.cmb_line_spacing.currentText())
        except ValueError:
            spacing = DEFAULT_LINE_SPACING

        self._display_font_size = size
        self._display_line_spacing = spacing

        font = QFont("Consolas", size)
        self.txt_rx.setFont(font)
        self.txt_tx_log.setFont(font)

        # 用 QTextOption 设置默认行间距，避免每次插入都操作文档格式导致崩溃
        option = QTextOption()
        option.setLineHeight(int(spacing * 100), 4)
        self.txt_rx.document().setDefaultTextOption(option)
        self.txt_tx_log.document().setDefaultTextOption(option)

    def on_display_setting_changed(self):
        self._apply_display_settings()

    def _apply_status(self, status: str):
        """更新状态指示灯和文字颜色"""
        if status == STATUS_CONNECTED:
            self.lbl_status_dot.setStyleSheet("color: #4caf50;")
            self.lbl_status.setStyleSheet("color: #4caf50;")
        elif status == STATUS_DISCONNECTED:
            self.lbl_status_dot.setStyleSheet("color: #9e9e9e;")
            self.lbl_status.setStyleSheet("color: #9e9e9e;")
        elif status == STATUS_ERROR:
            self.lbl_status_dot.setStyleSheet("color: #f44336;")
            self.lbl_status.setStyleSheet("color: #f44336;")

    def _connect_signals(self):
        self.btn_open.clicked.connect(self.on_open_clicked)
        self.btn_refresh.clicked.connect(self._refresh_ports)
        self.btn_send.clicked.connect(self.on_send_clicked)
        self.btn_clear_rx.clicked.connect(self.on_clear_rx_clicked)
        self.btn_save_rx.clicked.connect(self.on_save_rx_clicked)
        self.btn_clear_tx_log.clicked.connect(self.on_clear_tx_log_clicked)
        self.btn_browse.clicked.connect(self.on_browse_clicked)
        self.btn_save.clicked.connect(self.on_save_with_options_clicked)
        self.btn_hex_convert.clicked.connect(self.on_hex_convert_clicked)
        self.sig_rx_data.connect(self._on_rx_data_ui)
        self.sig_status.connect(self._on_status_ui)
        self.serial.set_rx_callback(self._on_rx_data_thread)
        # 实时参数更新（串口打开时生效）
        self.cmb_baud.currentTextChanged.connect(self.on_param_changed)
        self.cmb_data.currentTextChanged.connect(self.on_param_changed)
        self.cmb_stop.currentTextChanged.connect(self.on_param_changed)
        self.cmb_parity.currentTextChanged.connect(self.on_param_changed)

    def _refresh_ports(self):
        self.cmb_port.clear()
        try:
            ports = self.serial.list_ports()
            if ports:
                for p in ports:
                    device = p["device"]
                    desc = p["description"]
                    display = f"{device}  |  {desc[:25]}" if desc else device
                    self.cmb_port.addItem(display, device)
                self.cmb_port.setCurrentIndex(0)
            else:
                self.cmb_port.addItem("无可用串口", "")
        except Exception as e:
            self.cmb_port.addItem("扫描失败", "")
            self.lbl_status.setText(f"扫描串口失败: {e}")
            self._apply_status(STATUS_ERROR)

    def _get_selected_port(self) -> str:
        """获取当前选中的端口设备名"""
        data = self.cmb_port.currentData()
        if data:
            return str(data)
        text = self.cmb_port.currentText().strip()
        if "  |  " in text:
            return text.split("  |  ")[0]
        return text

    def on_open_clicked(self):
        if self.serial.is_open():
            self.serial.close()
            self.btn_open.setText("打开串口")
            self.lbl_status.setText(STATUS_DISCONNECTED)
            self._apply_status(STATUS_DISCONNECTED)
            self.btn_send.setEnabled(False)
            self.chk_timer.setChecked(False)
            return

        port = self._get_selected_port()
        if not port or port == "无可用串口" or port == "扫描失败":
            QMessageBox.warning(self, "提示", "请选择有效的串口号")
            return

        try:
            baud = int(self.cmb_baud.currentText())
        except ValueError:
            QMessageBox.warning(self, "错误", "波特率必须为整数")
            return

        data_bits = int(self.cmb_data.currentText())
        stop_bits = float(self.cmb_stop.currentText())
        parity = self.cmb_parity.currentText()

        if self.serial.open(port, baud, data_bits, stop_bits, parity):
            self.btn_open.setText("关闭串口")
            self.lbl_status.setText(f"{STATUS_CONNECTED} ({self.serial.get_port_info()})")
            self._apply_status(STATUS_CONNECTED)
            self.btn_send.setEnabled(True)
        else:
            err = self.serial.get_last_error()
            self.lbl_status.setText(STATUS_ERROR)
            self._apply_status(STATUS_ERROR)
            QMessageBox.critical(self, "打开失败", f"无法打开串口:\n{err}")

    def on_send_clicked(self):
        if not self.serial.is_open():
            return

        text = self.txt_tx.toPlainText()
        if not text:
            return

        if self.hex_tx:
            ok = self.serial.send_hex(text)
        else:
            ok = self.serial.send_string(text)
            if ok and self.chk_newline.isChecked():
                ok = self.serial.send(b"\r\n")

        if ok:
            data_len = len(text) if self.hex_tx else len(text.encode("utf-8"))
            if self.chk_newline.isChecked() and not self.hex_tx:
                data_len += 2
            self.tx_count += data_len
            self._update_stats()
            self._append_tx_log(text, self.hex_tx, self.chk_newline.isChecked() and not self.hex_tx)
        else:
            QMessageBox.warning(self, "发送失败", self.serial.get_last_error())

    def _on_rx_data_thread(self, data: bytes):
        self.sig_rx_data.emit(data)

    def _on_rx_data_ui(self, data: bytes):
        try:
            if self.chk_pause_rx.isChecked():
                return

            now = time.time()

            # 保存原始字节用于 HEX 切换时重新格式化
            self._raw_rx_bytes += data

            text = format_rx_data(data, self.hex_rx)

            # 时间戳
            if self.timestamp_enabled:
                ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                elapsed_ms = (now - self._last_rx_time) * 1000 if self._last_rx_time > 0 else float('inf')

                # 超时标记：距上次接收超过设定时间，插入分隔行
                if self.chk_timeout.isChecked() and self._last_rx_time > 0:
                    if elapsed_ms > self.timestamp_timeout:
                        text = f"\n--- [{ts}] timeout ({elapsed_ms:.0f}ms) ---\n{text}"

                # 帧间隔智能时间戳：仅在帧边界插入时间戳
                if self.frame_gap_enabled and self._last_rx_time > 0:
                    if elapsed_ms > self.frame_gap_ms:
                        # 新帧，插入时间戳（前面换行，末尾不换行，允许同帧数据连续追加）
                        text = f"\n[{ts}] {text}"
                    # else: 同一帧内，不加时间戳、不换行，直接追加
                else:
                    # 未启用帧间隔：原有行为，每条数据都带时间戳和换行
                    prefix = "\n" if self._last_rx_time > 0 else ""
                    text = f"{prefix}[{ts}] {text}\n"

            self._last_rx_time = now
            self.rx_buffer += text

            # 缓冲区超限时：打包旧数据到文件，清空缓冲区继续接收
            if len(self.rx_buffer) > self.max_rx_buffer:
                self._auto_backup_rx_buffer()
                self.rx_buffer = ""
                self._raw_rx_bytes = bytearray()
                self.txt_rx.clear()

            self._insert_to_editor(self.txt_rx, text)

            self.rx_count += len(data)
            self._update_stats()
        except Exception as e:
            # 槽函数异常保护：任何异常都不应导致 Qt 崩溃
            print(f"[ERROR] _on_rx_data_ui: {e}")

    def _on_status_ui(self, msg: str, color: str):
        self.lbl_status.setText(msg)
        self.lbl_status.setStyleSheet(f"color: {color};")

    def on_hex_rx_changed(self, state):
        """实时切换 HEX/ASCII 显示模式，保留历史数据"""
        self.hex_rx = state == Qt.CheckState.Checked.value
        mode = "HEX" if self.hex_rx else "ASCII"

        self.txt_rx.clear()
        self.rx_buffer = ""

        raw = bytes(self._raw_rx_bytes)
        if not raw:
            notice = f"[模式切换] 已切换为 {mode} 显示模式\n"
            self._insert_to_editor(self.txt_rx, notice)
            self.rx_buffer = notice
            return

        # 大数据量保护：只转换最后一部分，避免界面卡顿
        MAX_REFORMAT = 200 * 1024  # 200KB
        if len(raw) > MAX_REFORMAT:
            raw = raw[-MAX_REFORMAT:]
            notice = f"[模式切换] 已切换为 {mode} 显示模式（仅显示最近 200KB 原始数据）\n"
        else:
            notice = f"[模式切换] 已切换为 {mode} 显示模式\n"

        self._insert_to_editor(self.txt_rx, notice)
        self.rx_buffer = notice

        # 重新格式化原始字节
        text = format_rx_data(raw, self.hex_rx)
        if self.timestamp_enabled:
            ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            text = f"[{ts}] {text}"

        self.rx_buffer += text
        self._insert_to_editor(self.txt_rx, text)

    def on_hex_tx_changed(self, state):
        self.hex_tx = state == Qt.CheckState.Checked.value

    def on_show_tx_log_changed(self, state):
        checked = state == Qt.CheckState.Checked.value
        self.grp_tx_log.setVisible(checked)

    def on_param_changed(self):
        """串口打开状态下实时更新波特率/数据位/停止位/校验位"""
        if not self.serial.is_open():
            return

        try:
            baud = int(self.cmb_baud.currentText())
        except ValueError:
            return

        try:
            data_bits = int(self.cmb_data.currentText())
            stop_bits = float(self.cmb_stop.currentText())
        except ValueError:
            return

        parity = self.cmb_parity.currentText()

        if self.serial.update_params(baud, data_bits, stop_bits, parity):
            self.lbl_status.setText(f"{STATUS_CONNECTED} ({self.serial.get_port_info()})")
        else:
            err = self.serial.get_last_error()
            self.lbl_status.setText(STATUS_ERROR)
            self._apply_status(STATUS_ERROR)
            QMessageBox.critical(self, "参数更新失败", f"无法更新串口参数:\n{err}")

    def on_timestamp_changed(self, state):
        self.timestamp_enabled = state == Qt.CheckState.Checked.value

    def on_timeout_changed(self, state):
        pass

    def on_timeout_interval_changed(self, text: str):
        try:
            self.timestamp_timeout = int(text.strip())
        except ValueError:
            pass

    def on_frame_gap_changed(self, state):
        self.frame_gap_enabled = state == Qt.CheckState.Checked.value

    def on_frame_gap_interval_changed(self, text: str):
        try:
            self.frame_gap_ms = int(text.strip())
        except ValueError:
            pass

    def on_buffer_changed(self, text: str):
        """接收缓冲区大小变更"""
        try:
            cleaned = text.replace(",", "").strip()
            value = int(cleaned)
            if value < 1000:
                value = 1000
            elif value > 100000000:
                value = 100000000
            self.max_rx_buffer = value
        except ValueError:
            pass

    def _auto_backup_rx_buffer(self):
        """将当前接收缓冲区数据自动打包保存到文件，然后清空继续接收"""
        try:
            backup_dir = os.path.join(os.getcwd(), RX_BACKUP_DIR)
            os.makedirs(backup_dir, exist_ok=True)

            self._backup_counter += 1
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rx_backup_{timestamp}_{self._backup_counter:03d}.txt"
            filepath = os.path.join(backup_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.rx_buffer)

            file_size = os.path.getsize(filepath)
            size_str = f"{file_size / 1024:.1f} KB" if file_size < 1024 * 1024 else f"{file_size / (1024 * 1024):.2f} MB"

            # 在接收区插入提示信息
            notice = f"\n[自动备份] 缓冲区超限，已打包保存到 {filename} ({size_str})\n"
            self._insert_to_editor(self.txt_rx, notice)
            self._raw_rx_bytes = bytearray()
        except Exception as e:
            # 备份失败时截断旧数据，保证不阻塞接收
            self.rx_buffer = self.rx_buffer[-self.max_rx_buffer:]
            self._raw_rx_bytes = bytearray()

    def _insert_to_editor(self, editor: QTextEdit, text: str):
        """插入文本到末尾"""
        cursor = editor.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertPlainText(text)

    def _append_tx_log(self, text: str, is_hex: bool, has_newline: bool):
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        prefix = f"[{ts}] " if self.chk_tx_log_timestamp.isChecked() else ""
        display = text
        if has_newline:
            display += "\\r\\n"
        if is_hex:
            display = display.replace(" ", "").upper()
            display = " ".join(display[i:i+2] for i in range(0, len(display), 2))
        log_line = f"{prefix}{display}\n"
        self._insert_to_editor(self.txt_tx_log, log_line)

    def on_clear_tx_log_clicked(self):
        self.txt_tx_log.clear()

    def on_clear_rx_clicked(self):
        self.txt_rx.clear()
        self.rx_buffer = ""
        self._raw_rx_bytes = bytearray()
        self.rx_count = 0
        self._last_rx_time = 0.0
        self._update_stats()

    def on_save_rx_clicked(self):
        path, _ = QFileDialog.getSaveFileName(self, "保存接收数据", "rx_data.txt", "Text Files (*.txt)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.txt_rx.toPlainText())
            QMessageBox.information(self, "保存成功", f"数据已保存到:\n{path}")

    def on_browse_clicked(self):
        fmt_idx = self.cmb_save_fmt.currentIndex()
        if fmt_idx == 2:
            path, _ = QFileDialog.getSaveFileName(self, "保存数据", "rx_data.bin", "Binary Files (*.bin)")
        else:
            path, _ = QFileDialog.getSaveFileName(self, "保存数据", "rx_data.txt", "Text Files (*.txt)")
        if path:
            self.edt_save_path.setText(path)

    def on_save_with_options_clicked(self):
        path = self.edt_save_path.text().strip()
        if not path:
            QMessageBox.warning(self, "提示", "请先选择保存路径")
            return

        fmt_idx = self.cmb_save_fmt.currentIndex()
        try:
            if fmt_idx == 0:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self.txt_rx.toPlainText())
            elif fmt_idx == 1:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self.txt_rx.toPlainText())
            elif fmt_idx == 2:
                with open(path, "wb") as f:
                    f.write(self.txt_rx.toPlainText().encode("utf-8", errors="replace"))
            QMessageBox.information(self, "保存成功", f"数据已保存到:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "保存失败", str(e))

    def on_hex_convert_clicked(self):
        text_in = self.txt_hex_in.toPlainText()
        if not text_in:
            self.txt_hex_out.clear()
            return

        direction = self.cmb_hex_dir.currentIndex()
        try:
            if direction == 0:
                result = str_to_hex(text_in)
            else:
                if not is_valid_hex(text_in):
                    self.txt_hex_out.setPlainText("错误：输入的不是合法 HEX 格式")
                    return
                result = hex_to_str(text_in)
            self.txt_hex_out.setPlainText(result)
        except Exception as e:
            self.txt_hex_out.setPlainText(f"转换错误: {e}")

    def on_timer_toggled(self, checked: bool):
        if checked:
            if not self.serial.is_open():
                QMessageBox.warning(self, "提示", "请先打开串口")
                self.chk_timer.setChecked(False)
                return
            try:
                interval = int(self.cmb_interval.currentText())
            except ValueError:
                QMessageBox.warning(self, "错误", "定时间隔必须为整数")
                self.chk_timer.setChecked(False)
                return
            self.timer_send.start(interval)
        else:
            self.timer_send.stop()

    def _update_stats(self):
        self.lbl_stats.setText(f"RX: {self.rx_count} bytes  |  TX: {self.tx_count} bytes")

    def closeEvent(self, event):
        self.serial.close()
        self._save_settings()
        event.accept()

    def _settings_path(self) -> str:
        # 打包后：exe 所在目录；开发时：源码所在目录
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, ".settings.json")

    def _load_settings(self):
        """加载上次的串口参数缓存"""
        path = self._settings_path()
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                cfg = json.load(f)

            port = cfg.get("port", "")
            baud = cfg.get("baud", str(DEFAULT_BAUD))
            data = cfg.get("data_bits", str(DEFAULT_DATA_BITS))
            stop = cfg.get("stop_bits", str(DEFAULT_STOP_BITS))
            parity = cfg.get("parity", DEFAULT_PARITY)
            buf = cfg.get("buffer", str(DEFAULT_RX_BUFFER))
            interval = cfg.get("timer_interval", str(DEFAULT_TIMER_INTERVAL))
            hex_rx = cfg.get("hex_rx", False)
            hex_tx = cfg.get("hex_tx", False)
            ts = cfg.get("timestamp", False)
            timeout = cfg.get("timeout", False)
            frame_gap = cfg.get("frame_gap", False)
            frame_gap_ms = cfg.get("frame_gap_ms", str(DEFAULT_FRAME_GAP))
            font_size = cfg.get("font_size", str(DEFAULT_FONT_SIZE))
            line_spacing = cfg.get("line_spacing", str(DEFAULT_LINE_SPACING))
            newline = cfg.get("newline", False)

            # 串口号：如果在列表中就选中，否则设为当前文本
            idx = self.cmb_port.findText(port)
            if idx >= 0:
                self.cmb_port.setCurrentIndex(idx)
            elif port:
                self.cmb_port.setCurrentText(port)

            self.cmb_baud.setCurrentText(baud)
            self.cmb_data.setCurrentText(data)
            self.cmb_stop.setCurrentText(stop)
            self.cmb_parity.setCurrentText(parity)
            self.cmb_buffer.setCurrentText(buf)
            self.cmb_interval.setCurrentText(interval)

            if hex_rx:
                self.chk_hex_rx.setChecked(True)
            if hex_tx:
                self.chk_hex_tx.setChecked(True)
            if ts:
                self.chk_timestamp.setChecked(True)
            if timeout:
                self.chk_timeout.setChecked(True)
            if frame_gap:
                self.chk_frame_gap.setChecked(True)
            if frame_gap_ms:
                self.cmb_frame_gap.setCurrentText(frame_gap_ms)
            if font_size:
                self.cmb_font_size.setCurrentText(font_size)
            if line_spacing:
                self.cmb_line_spacing.setCurrentText(line_spacing)
            if newline:
                self.chk_newline.setChecked(True)
        except Exception:
            pass

    def _save_settings(self):
        """保存当前串口参数到缓存"""
        try:
            cfg = {
                "port": self.cmb_port.currentText().strip(),
                "baud": self.cmb_baud.currentText().strip(),
                "data_bits": self.cmb_data.currentText().strip(),
                "stop_bits": self.cmb_stop.currentText().strip(),
                "parity": self.cmb_parity.currentText().strip(),
                "buffer": self.cmb_buffer.currentText().strip(),
                "timer_interval": self.cmb_interval.currentText().strip(),
                "hex_rx": self.chk_hex_rx.isChecked(),
                "hex_tx": self.chk_hex_tx.isChecked(),
                "timestamp": self.chk_timestamp.isChecked(),
                "timeout": self.chk_timeout.isChecked(),
                "frame_gap": self.chk_frame_gap.isChecked(),
                "frame_gap_ms": self.cmb_frame_gap.currentText().strip(),
                "font_size": self.cmb_font_size.currentText().strip(),
                "line_spacing": self.cmb_line_spacing.currentText().strip(),
                "newline": self.chk_newline.isChecked(),
            }
            with open(self._settings_path(), "w", encoding="utf-8") as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)
        except Exception:
            pass


def _create_app_icon() -> QIcon:
    """用 QPainter 绘制应用图标（无需外部文件）"""
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 外圆
    painter.setPen(QPen(QColor("#2196F3"), 4))
    painter.setBrush(QBrush(QColor("#e3f2fd")))
    painter.drawEllipse(4, 4, 56, 56)

    # 内部 "TX" 字样
    painter.setPen(QPen(QColor("#1565C0"), 2))
    font = QFont("Microsoft YaHei", 14, QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(QRect(0, 0, size, size), Qt.AlignmentFlag.AlignCenter, "TX")

    painter.end()
    return QIcon(pixmap)


def run():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(_create_app_icon())
    win = MainWindow()
    win.setWindowIcon(_create_app_icon())
    win.show()
    sys.exit(app.exec())
