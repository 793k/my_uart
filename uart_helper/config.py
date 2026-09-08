"""
config.py — 串口助手全局配置与常量
"""

# 串口参数选项
BAUD_RATES = [1200, 2400, 4800, 9600, 14400, 19200, 38400, 56000, 57600,
              115200, 128000, 230400, 256000, 460800, 500000, 512000,
              576000, 600000, 750000, 921600, 1000000, 1152000,
              1500000, 2000000, 2500000, 3000000, 3500000, 4000000]
DATA_BITS = [5, 6, 7, 8]
STOP_BITS = [1, 1.5, 2]
PARITY_OPTIONS = ["None", "Even", "Odd", "Mark", "Space"]

# 默认参数
DEFAULT_BAUD = 115200
DEFAULT_DATA_BITS = 8
DEFAULT_STOP_BITS = 1
DEFAULT_PARITY = "None"

# 定时发送间隔选项 (ms)
TIMER_INTERVALS = [10, 50, 100, 200, 500, 1000, 2000, 5000]
DEFAULT_TIMER_INTERVAL = 1000

# 接收缓冲区大小选项 (字节)
RX_BUFFER_OPTIONS = [50000, 100000, 200000, 500000,
                     1000000, 2000000, 5000000, 10000000]
DEFAULT_RX_BUFFER = 500000

# 原始字节缓存上限：仅用于 HEX/ASCII 显示模式切换时的历史回看，
# 超过则丢弃最旧字节，防止长时运行（尤其 A5 解析模式）内存无界增长
RAW_RX_CACHE_BYTES = 2 * 1024 * 1024

# 自动打包备份目录
RX_BACKUP_DIR = "rx_backup"

# 本地缓存根目录（位于系统"文档"目录下，由 app_cache.py 管理）
CACHE_FOLDER_NAME = "UART_Helper"

# 时间戳超时间隔选项 (ms)
TIMESTAMP_TIMEOUT_OPTIONS = [100, 500, 1000, 2000, 5000, 10000]
DEFAULT_TIMESTAMP_TIMEOUT = 1000

# 帧间隔阈值选项 (ms) — 用于智能时间戳：同一帧内仅显示一次时间戳
FRAME_GAP_OPTIONS = [1, 2, 5, 10, 20, 50, 100]
DEFAULT_FRAME_GAP = 10

# 空闲自动关闭串口：UI 无鼠标/键盘操作超过设定时长即自动关闭串口（分钟）
IDLE_CLOSE_OPTIONS = [1, 5, 10, 15, 30, 60]
DEFAULT_IDLE_CLOSE_MINUTES = 15

# UI 配置
WINDOW_TITLE = "UART 串口助手"
WINDOW_MIN_SIZE = (900, 650)

# 版本信息（左下角显示；发布新版时更新版本号与时间）
APP_VERSION = "2.3"
APP_UPDATE_TIME = "2026-09-08"

# 显示设置
DEFAULT_FONT_SIZE = 11
DEFAULT_LINE_SPACING = 1.5

# 状态文本
STATUS_CONNECTED = "已连接"
STATUS_DISCONNECTED = "未连接"
STATUS_ERROR = "错误"
