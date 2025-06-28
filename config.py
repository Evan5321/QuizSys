# 应用配置
APP_NAME = "历史大事年表背诵助手"
APP_VERSION = "1.0.0"

# 数据文件配置
DATA_FILE = "history_events.json"
STATS_FILE = "user_stats.json"

# 学习配置
DEFAULT_SESSION_QUESTIONS = 10  # 默认每次会话的问题数量
MAX_SESSION_QUESTIONS = 50      # 最大每次会话的问题数量

# 复习算法配置
MIN_EASE_FACTOR = 1.3           # 最小难度系数
INITIAL_EASE_FACTOR = 2.5       # 初始难度系数
INITIAL_INTERVAL = 1            # 初始间隔（天）