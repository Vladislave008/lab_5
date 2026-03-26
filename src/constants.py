class COLORS:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BLACK = '\033[90m'
    ORANGE = '\033[38;5;208m'
    PINK = '\033[38;5;206m'
    GRAY = '\033[38;5;240m'
    LIGHT_BLUE = '\033[38;5;45m'
    BROWN = '\033[38;5;130m'
    RESET = '\033[0m'

TASK_STATUS_VALUES = ["created", "started", "finished"]
TASK_PRIORITY_LOWER = 0
TASK_PRIORITY_UPPER = 10
ALLOWED_TASK_ATTRIBUTES = [
    "payload", "is_ready",
    "created_at", "id", "priority", "status", 
    "planned_time", "description", "duration",
    "started_at", "finished_at", "is_valid"
]