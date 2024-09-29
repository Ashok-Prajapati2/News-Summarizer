import logging
import os
from logging.handlers import RotatingFileHandler

# Define log directory and file
log_dir = "logs"
log_file = "app.log"

# Create log directory if it doesn't exist
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Set up a rotating log handler (5MB per file, up to 5 files)
log_handler = RotatingFileHandler(
    filename=os.path.join(log_dir, log_file), 
    maxBytes=5*1024*1024,  # 5MB
    backupCount=5
)

# Define log format
log_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

log_handler.setFormatter(log_format)

# Set up the logger
logger = logging.getLogger("app_logger")
logger.setLevel(logging.DEBUG)  # Log all levels (DEBUG and above)
logger.addHandler(log_handler)

# Optional: log to console as well
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)
logger.addHandler(console_handler)

# Avoid logging multiple times if this file is imported multiple times
logger.propagate = False
