from datetime import datetime

def log(message: str, level: str = "INFO") -> None:
    """
    Logs a message with a timestamp and level.

    Args:
        message (str): The message to log.
        level (str, optional): The log level. Defaults to "INFO".
    """
    timestamp = str(datetime.now())[:-3]

    for line in message.splitlines():
        print(f"[{timestamp}:{level}: {line}]")