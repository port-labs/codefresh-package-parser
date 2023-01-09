import sys
from app.utils import normalize_package_filters, normalize_identifier
from app.port import upsert_port_entity
import logging
import xmltodict
from app.consts import PACKAGE_RELEASE_BLUEPRINT_IDENTIFIER, PACKAGE_BLUEPRINT_IDENTIFIER
sys.path.append('../')


logger = logging.getLogger('packageparser.parser.c_sharp')


def parse_packages_from_c_sharp_package_files(port_access_token, package_file_path_list, package_filters):
    packages_results = []
    normalized_filters = normalize_package_filters(package_filters.split(','))
    logger.info(f'Filters are: {normalized_filters}')
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
    # If there is only a single package in the .csproj file, the packages_array variable is a dictionary and not an array
    if isinstance(packages_array, dict):
        packages_array = [packages_array]
    for package_reference in packages_array:
        internal_package = False
        logger.debug(f'Looking at package: {package_reference["@Include"]}')
        if any(filter in package_reference['@Include'].lower() for filter in packages_filters):
            internal_package = True
        logger.debug(f'Package {package_reference["@Include"]} is internal: {internal_package}')
        package_id = normalize_identifier(package_reference['@Include'])
        logger.debug(f'Normalized package identifier: {package_id}')
        upsert_port_entity(port_access_token, PACKAGE_BLUEPRINT_IDENTIFIER, {
            'identifier': package_id,
            'title': package_id,
            "properties": {
                "Language": package_language,
                "Internal": internal_package
            }
        })
        package_release_id = f'{package_id}_{normalize_identifier(package_reference["@Version"])}'
        logger.debug(f'Normalized release identifier: {package_release_id}')
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
