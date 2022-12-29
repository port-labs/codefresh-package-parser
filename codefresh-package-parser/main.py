#!/usr/bin/env python3

import json
import os

from port import get_access_token
from git_client import get_file_contents

from utils import validate_and_load_env_vars

from package_parser import parse_packages_based_on_manager_type

OUTPUT_DIR = "/tmp/packagevars/"


def main():
    REPO_URL, ACCESS_TOKEN, PORT_CLIENT_ID, PORT_CLIENT_SECRET, PACKAGE_MANAGER, PACKAGES_FILE_PATH, PACKAGE_FILTER_STRING = validate_and_load_env_vars()
    packages_file_content = get_file_contents(REPO_URL, ACCESS_TOKEN, PACKAGES_FILE_PATH)
    access_token = get_access_token(PORT_CLIENT_ID, PORT_CLIENT_SECRET)
    packages_dict = parse_packages_based_on_manager_type(
        access_token, PACKAGE_MANAGER, packages_file_content, PACKAGE_FILTER_STRING)
    print(packages_dict)
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
    print(name + "=" + value_str)


if __name__ == "__main__":
    main()
