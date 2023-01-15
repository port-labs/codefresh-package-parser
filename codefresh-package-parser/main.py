#!/usr/bin/env python3

import json
import os
import logging

from app.port import get_access_token
from app.consts import CLIENT_ID_KEY, CLIENT_SECRET_KEY, ACCESS_TOKEN_KEY
from app.git_client import clone_repo_and_map_files
from app.log_utils import log_file_handler, log_stream_handler

from app.utils import validate_and_load_env_vars
from app.port import upsert_port_entity, get_port_entity

from app.parsers.package_parser import parse_packages_based_on_manager_type

logging.basicConfig(handlers=[log_file_handler, log_stream_handler], level=logging.DEBUG)

logger = logging.getLogger('package_parser.main')

OUTPUT_DIR = "/tmp/packagevars/"


def main():
    REPO_URL, GIT_PROVIDER_USERNAME, GIT_PROVIDER_APP_PASSWORD, PORT_CLIENT_ID, PORT_CLIENT_SECRET, PACKAGE_MANAGER, PACKAGES_FILE_FILTER, INTERNAL_PACKAGE_FILTERS = validate_and_load_env_vars()
    port_credentials = {
        CLIENT_ID_KEY: PORT_CLIENT_ID,
        CLIENT_SECRET_KEY: PORT_CLIENT_SECRET,
        ACCESS_TOKEN_KEY: get_access_token(PORT_CLIENT_ID, PORT_CLIENT_SECRET)
    }
    package_file_path_list = clone_repo_and_map_files(REPO_URL, GIT_PROVIDER_USERNAME, GIT_PROVIDER_APP_PASSWORD, PACKAGES_FILE_FILTER)
    packages_array = parse_packages_based_on_manager_type(
        port_credentials, PACKAGE_MANAGER, package_file_path_list, INTERNAL_PACKAGE_FILTERS)
    logger.info(f'packages_dict={packages_array}')
    TARGET_BLUEPRINT_IDENTIFIER = os.getenv('TARGET_BLUEPRINT_IDENTIFIER', None)
    TARGET_ENTITY_IDENTIFIER = os.getenv('TARGET_ENTITY_IDENTIFIER', None)
    if TARGET_BLUEPRINT_IDENTIFIER and TARGET_ENTITY_IDENTIFIER:
        curr_props = get_port_entity(port_credentials, TARGET_BLUEPRINT_IDENTIFIER, TARGET_ENTITY_IDENTIFIER)
        body = {
            'identifier': TARGET_ENTITY_IDENTIFIER,
            'properties': curr_props['entity']['properties'],
            'relations': {
                'library-releases': packages_array
            }
        }
        upsert_port_entity(port_credentials, TARGET_BLUEPRINT_IDENTIFIER, body)
    # Create output dir
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Generate output files from payload
    output_content_to_files(packages_array)


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
