import logging
import structlog
from django.conf import settings


def configure_logging():
    """
    Configure the logging settings using both `logging` and `structlog` for structured logs.
    """
    log_level = logging.DEBUG if settings.DEBUG else logging.ERROR

    # Configure the base logging settings
    logging.basicConfig(
        format="%(message)s",  # Customize the format of the log messages
        level=log_level,       # Set the log level to DEBUG or ERROR based on settings.DEBUG
    )

    # Configure structlog to output structured logs in JSON format with timestamp, log level, and more.
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),         # Add timestamp
            structlog.stdlib.add_log_level,                      # Add log level (INFO, ERROR, etc.)
            structlog.processors.format_exc_info,                # Format exception info
            structlog.processors.StackInfoRenderer(),            # Render stack trace info
            structlog.processors.JSONRenderer(),                 # Render logs in JSON format
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        # Use bound logger for better performance
        wrapper_class=structlog.stdlib.BoundLogger,  # type: ignore[arg-type]
        # Cache logger to optimize performance
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = None):
    """
    Return a structured logger instance.
    """
    return structlog.get_logger(name)


class Logger:
    """
    A wrapper class for structlog's logger that allows us to log messages with different severity levels.
    """
    def __init__(self):
        # Initialize the structlog logger
        self.logger = structlog.get_logger()

    def info(self, message, **extra):
        """
        Log an info level message.
        """
        self.logger.info(message, **extra)

    def warning(self, message, **extra):
        """
        Log a warning level message.
        """
        self.logger.warning(message, **extra)

    def error(self, message, **extra):
        """
        Log an error level message.
        """
        self.logger.error(message, **extra)

    def exception(self, message, **extra):
        """
        Log an exception level message (with traceback).
        """
        self.logger.exception(message, **extra)


# Create a logger instance that can be used across the project
logger = Logger()




