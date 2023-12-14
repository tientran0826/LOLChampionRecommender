import logging
from constants import LOG_DIR
# Configure the root logger to log INFO and higher level messages
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    datefmt="%d-%b-%y %H:%M:%S")

# Create a logger for the 'status.log'
status_logger = logging.getLogger('status_logger')
status_logger.setLevel(logging.INFO)

# Configure the 'status.log' file handler
status_handler = logging.FileHandler(LOG_DIR + 'status.log')
status_handler.setLevel(logging.INFO)
status_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S"))

# Add the handler to the 'status_logger'
status_logger.addHandler(status_handler)

# Create a separate logger for the 'errors.log'
error_logger = logging.getLogger('error_logger')
error_logger.setLevel(logging.ERROR)

# Configure the 'errors.log' file handler
error_handler = logging.FileHandler(LOG_DIR + 'errors.log')
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S"))

# Add the handler to the 'error_logger'
error_logger.addHandler(error_handler)

# Create a stream handler to output logs to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S"))

# # Add the console handler to the root logger
# logging.getLogger().addHandler(console_handler)

class log:
    def info(text):
        status_logger.info(text)
    def exception(text):
        error_logger.exception(text)