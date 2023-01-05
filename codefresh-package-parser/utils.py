import logging

import os

from consts import SUPPORTED_PACKAGE_MANAGERS

logger = logging.getLogger('package_parser:package_parser_utils')


def validate_and_load_env_vars():
    REPO_URL = os.getenv('REPO_URL', None)
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN', None)
    PORT_CLIENT_ID = os.getenv('PORT_CLIENT_ID', None)
    PORT_CLIENT_SECRET = os.getenv('PORT_CLIENT_SECRET', None)
    PACKAGE_MANAGER = os.getenv('PACKAGE_MANAGER', None)
    PACKAGES_FILE_FILTER = os.getenv('PACKAGES_FILE_FILTER', None)
    INTERNAL_PACKAGE_FILTERS = os.getenv('INTERNAL_PACKAGE_FILTERS', None)

    result = tuple((REPO_URL, ACCESS_TOKEN, PORT_CLIENT_ID, PORT_CLIENT_SECRET, PACKAGE_MANAGER, PACKAGES_FILE_FILTER, INTERNAL_PACKAGE_FILTERS))
    for var in result:
        if var is None:
            logger.error(f'One of the required parameters - REPO_URL, ACCESS_TOKEN, PORT_CLIENT_ID, PORT_CLIENT_SECRET, PACKAGE_MANAGER, PACKAGES_FILE_FILTER, INTERNAL_PACKAGE_FILTERS is missing')
            exit(1)

    if PACKAGE_MANAGER not in SUPPORTED_PACKAGE_MANAGERS:
        logger.error(
            f'Invalid package manager: {PACKAGE_MANAGER} provided, available values are: {"".join(f"{str(x)}, " for x in SUPPORTED_PACKAGE_MANAGERS)}')
        exit(1)

    return result


def normalize_identifier(original_identifier: str):
    return original_identifier.replace('.', '-')


def normalize_package_filters(package_filters: list[str]):
    return [x.lower() for x in package_filters]
