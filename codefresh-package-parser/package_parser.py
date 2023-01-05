import sys

from utils import normalize_identifier, normalize_package_filters
from port import get_port_entity, upsert_port_entity
import xmltodict
import logging

logger = logging.getLogger('package_parser.parser')


PACKAGE_BLUEPRINT_IDENTIFIER = 'library'
PACKAGE_RELEASE_BLUEPRINT_IDENTIFIER = 'library-release'


def parse_packages_based_on_manager_type(port_access_token, package_manager_type, package_file_path_list, packages_filters):
    if package_manager_type == 'C_SHARP':
        logger.debug('Parsing C# packages')
        return parse_packages_from_c_sharp_package_files(port_access_token, package_file_path_list, packages_filters)
    elif package_manager_type == 'NPM':
        logger.debug('Parsing NPM packages')
        return []
    elif package_manager_type == 'JAVA':
        logger.debug('Parsing Java packages')
        return []


def parse_packages_from_c_sharp_package_files(port_access_token, package_file_path_list, package_filters):
    packages_results = []
    normalized_filters = normalize_package_filters(package_filters.split(','))
    for filter in normalized_filters:
        logger.info(f'Filter is: {filter}')
    for package_file_path in package_file_path_list:
        logger.debug(f'Parsing packages from file: {package_file_path}')
        with open(package_file_path) as f:
            project_structure_dict = xmltodict.parse(f.read())
            packages_results = packages_results + parse_packages_from_c_sharp_proj(port_access_token, project_structure_dict, normalized_filters)
    return packages_results


def parse_packages_from_c_sharp_proj(port_access_token, project_structure_dict, package_filters):
    packages_results = []
    item_groups_array = project_structure_dict['Project']['ItemGroup']

    for item_group in item_groups_array:
        if 'PackageReference' in item_group:
            packages_array = item_group['PackageReference']
            packages_results = packages_results + parse_packages_from_c_sharp_item_group(
                port_access_token, packages_array, package_filters)

    return packages_results


def parse_packages_from_c_sharp_item_group(port_access_token, packages_array, packages_filters: str):
    package_language = "C#"
    packages_results = []
    for package_reference in packages_array:
        internal_package = False
        logger.debug(f'Looking at package: {package_reference["@Include"]}')
        if any(filter in package_reference['@Include'].lower() for filter in packages_filters):
            internal_package = True
        logger.debug(f'Package {package_reference["@Include"]} is internal: {internal_package}')
        package_id = normalize_identifier(package_reference['@Include'])
        upsert_port_entity(port_access_token, PACKAGE_BLUEPRINT_IDENTIFIER, {
            'identifier': package_id,
            'title': package_id,
            "properties": {
                "Language": package_language,
                "Internal": internal_package
            }
        })
        package_release_id = f'{package_id}_{normalize_identifier(package_reference["@Version"])}'
        upsert_port_entity(port_access_token, PACKAGE_RELEASE_BLUEPRINT_IDENTIFIER, {
            'identifier': package_release_id,
            'title': package_release_id,
            "properties": {
                "Version": package_reference["@Version"]
            },
            "relations": {
                "library": package_id
            }

        })
        packages_results.append(package_release_id)
    return packages_results


def check_if_package_exists_in_port(port_access_token, blueprint_identifier, package_identifier):
    if get_port_entity(port_access_token, blueprint_identifier, package_identifier):
        return True
    return False
