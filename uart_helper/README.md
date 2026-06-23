# UART 串口助手

基于 Python + PyQt6 的模块化串口调试工具，便于扩展和定制需求。

## 文件结构

```
uart_helper/
├── main.py          # 入口文件，直接运行
├── config.py        # 全局配置与常量（波特率选项、缓冲区大小等）
├── serial_core.py   # 串口核心逻辑（无 UI 依赖，可单独测试）
├── ui_main.py       # 主窗口界面与交互
├── utils.py         # 工具函数（字节/HEX/ASCII 转换）
└── requirements.txt # 依赖列表
```

## 运行方式

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行
python main.py
```

## 模块化设计说明

| 文件 | 职责 | 扩展场景 |
|------|------|----------|
| `config.py` | 所有常量与默认值 | 新增波特率、修改缓冲区大小 |
| `serial_core.py` | 纯串口操作，线程安全 | 增加流控、添加校验算法、扩展协议层 |
| `ui_main.py` | 界面布局与信号槽 | 新增控件、调整布局、增加菜单栏 |
| `utils.py` | 数据格式转换 | 新增编码格式、添加解析器 |

## 如何添加新需求

**示例：在发送区添加自定义命令按钮**

1. 在 `ui_main.py` 的 `_build_ui()` 中新增按钮：
```python
self.btn_cmd_a = QPushButton("发送指令A")
v3.addWidget(self.btn_cmd_a)
```

2. 在 `_connect_signals()` 中绑定槽函数：
```python
self.btn_cmd_a.clicked.connect(self.on_cmd_a_clicked)
```

3. 添加处理函数：
```python
def on_cmd_a_clicked(self):
    self.txt_tx.setPlainText("01 03 00 00 00 0A")
    self.on_send_clicked()
```

**示例：修改默认波特率**

直接编辑 `config.py`：
```python
DEFAULT_BAUD = 9600
```

**示例：在 serial_core 中增加 MODBUS CRC 校验**

在 `serial_core.py` 的 `SerialCore` 类中添加 CRC 计算函数，然后在 `send_hex()` 中自动附加 CRC 字节即可。

## 当前功能

- 串口扫描与打开/关闭
- 波特率/数据位/停止位/校验位设置
- ASCII / HEX 接收显示切换
- ASCII / HEX 发送
- 发送新行（`\r\n`）
- 定时循环发送
- 接收暂停
- 清空/保存接收数据
- 收发字节统计
