import logging
import sys

# output_file_handler = logging.handlers.RotatingFileHandler(filename='logs/logs.logger',
#                                                            mode='a')
# stdout_handler = logging.StreamHandler(sys.stdout)

logging.basicConfig(
#   	#format="%(asctime)s %(name)-15s %(levelname)-6s %(message)s",
#     #datefmt="%y-%m-%d %H:%M:%S",
#     handlers=[
#     	output_file_handler,
#         stdout_handler
#     ]
)

logger = logging.getLogger('Logger')
logger.setLevel(logging.DEBUG)