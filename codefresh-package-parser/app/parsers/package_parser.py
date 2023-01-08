import logging

from app.parsers.c_sharp_parser import parse_packages_from_c_sharp_package_files
from app.parsers.npm_parser import parse_packages_from_npm_package_files


logger = logging.getLogger('package_parser.parser')


def parse_packages_based_on_manager_type(port_access_token, package_manager_type, package_file_path_list, packages_filters):
    if package_manager_type == 'C_SHARP':
        logger.info('Parsing C# packages')
        return parse_packages_from_c_sharp_package_files(port_access_token, package_file_path_list, packages_filters)
    elif package_manager_type == 'NPM':
        logger.info('Parsing NPM packages')
        return parse_packages_from_npm_package_files(port_access_token, package_file_path_list, packages_filters)
    elif package_manager_type == 'JAVA':
        logger.info('Parsing Java packages')
        return []
