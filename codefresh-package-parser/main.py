#!/usr/bin/env python3

import json
import os
import logging
import sys

from app.port import get_access_token
from app.git_client import clone_repo_and_map_files
from app.log_utils import log_file_handler, log_stream_handler

from app.utils import validate_and_load_env_vars

from app.parsers.package_parser import parse_packages_based_on_manager_type

logging.basicConfig(handlers=[log_file_handler, log_stream_handler], level=logging.DEBUG)

logger = logging.getLogger('package_parser.main')

OUTPUT_DIR = "/tmp/packagevars/"


def main():
    REPO_URL, GIT_PROVIDER_USERNAME, GIT_PROVIDER_APP_PASSWORD, PORT_CLIENT_ID, PORT_CLIENT_SECRET, PACKAGE_MANAGER, PACKAGES_FILE_FILTER, INTERNAL_PACKAGE_FILTERS = validate_and_load_env_vars()
    package_file_path_list = clone_repo_and_map_files(REPO_URL, GIT_PROVIDER_USERNAME, GIT_PROVIDER_APP_PASSWORD, PACKAGES_FILE_FILTER)
    access_token = get_access_token(PORT_CLIENT_ID, PORT_CLIENT_SECRET)
    packages_dict = parse_packages_based_on_manager_type(
        access_token, PACKAGE_MANAGER, package_file_path_list, INTERNAL_PACKAGE_FILTERS)
    logger.info(f'packages_dict={packages_dict}')
    # Create output dir
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Generate output files from payload
    output_content_to_files(packages_dict)


def output_content_to_files(payload_dict):
    write_var_file("PARSED_PACKAGES_ARRAY", payload_dict)


def write_var_file(name, value):
    # Make sure value isn't null
    if not value:
        value = ""
    # Cast array and boolean values to string
    # value_str = str(value)
    value_str = json.dumps(value)
    # Write the value to output file
    with open(OUTPUT_DIR + name, 'w') as file:
        file.write(value_str)
    logger.info(name + "=" + value_str)


if __name__ == "__main__":
    main()
