import logging

import os

logger = logging.getLogger('package_parser_utils')


def validate_and_load_env_vars():
    REPO_URL = os.getenv('REPO_URL', None)
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN', None)
    PORT_CLIENT_ID = os.getenv('PORT_CLIENT_ID', None)
    PORT_CLIENT_SECRET = os.getenv('PORT_CLIENT_SECRET', None)
    PACKAGE_MANAGER = os.getenv('PACKAGE_MANAGER', None)
    PACKAGES_FILE_PATH = os.getenv('PACKAGES_FILE_PATH', None)
    INTERNAL_PACKAGE_FILTER_STRING = os.getenv('INTERNAL_PACKAGE_FILTER_STRING', None)

    result = tuple((REPO_URL, ACCESS_TOKEN, PORT_CLIENT_ID, PORT_CLIENT_SECRET, PACKAGE_MANAGER, PACKAGES_FILE_PATH, INTERNAL_PACKAGE_FILTER_STRING))
    for var in result:
        if var is None:
            logger.error(f'One of the required parameters - REPO_URL, ACCESS_TOKEN, PORT_CLIENT_ID, PORT_CLIENT_SECRET, PACKAGE_MANAGER, PACKAGES_FILE_PATH, PACKAGE_FILTER_STRING is missing')
            exit(1)
    return result


def normalize_identifier(original_identifier: str):
    return original_identifier.replace('.', '-')
