import logging
import sys

formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s')
log_file_handler = logging.FileHandler('package_parser.log', mode='w', encoding='utf-8')
log_file_handler.setLevel(logging.DEBUG)
log_file_handler.setFormatter(formatter)
log_stream_handler = logging.StreamHandler(sys.stdout)
log_stream_handler.setLevel(logging.INFO)
log_stream_handler.setFormatter(formatter)
