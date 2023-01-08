from app.utils import normalize_package_filters, normalize_identifier
from app.port import upsert_port_entity
import logging
import json
from app.consts import PACKAGE_RELEASE_BLUEPRINT_IDENTIFIER, PACKAGE_BLUEPRINT_IDENTIFIER


logger = logging.getLogger('packageparser.parser.npm')


def parse_packages_from_npm_package_files(port_access_token, package_file_path_list, package_filters):
    packages_results = []
    normalized_filters = normalize_package_filters(package_filters.split(','))
    logger.info(f'Filters are: {normalized_filters}')
    for package_file_path in package_file_path_list:
        logger.debug(f'Parsing packages from file: {package_file_path}')
        with open(package_file_path) as f:
            project_structure_dict = json.load(f)
            packages_results = packages_results + parse_packages_from_package_json(port_access_token, project_structure_dict, normalized_filters)
    return packages_results


def parse_packages_from_package_json(port_access_token, project_structure_dict, package_filters):
    packages_results = []
    dependencies = project_structure_dict['dependencies']
    dev_dependencies = project_structure_dict['devDependencies']
    packages_results = packages_results + parse_packages_from_dependency_group(port_access_token, dependencies, package_filters)
    packages_results = packages_results + parse_packages_from_dependency_group(port_access_token, dev_dependencies, package_filters)

    return packages_results


def parse_packages_from_dependency_group(port_access_token, dependencies, packages_filters: str):
    package_language = "Node"
    packages_results = []
    for package_name, version in dependencies.items():
        internal_package = False
        logger.debug(f'Looking at package: {package_name}')
        if any(filter in package_name.lower() for filter in packages_filters):
            internal_package = True
        logger.debug(f'Package {package_name} is internal: {internal_package}')
        package_id = normalize_identifier(package_name)
        logger.debug(f'Normalized package identifier: {package_id}')
        upsert_port_entity(port_access_token, PACKAGE_BLUEPRINT_IDENTIFIER, {
            'identifier': package_id,
            'title': package_id,
            "properties": {
                "Language": package_language,
                "Internal": internal_package
            }
        })
        package_release_id = f'{package_id}_{normalize_identifier(version)}'
        logger.debug(f'Normalized release identifier: {package_release_id}')
        upsert_port_entity(port_access_token, PACKAGE_RELEASE_BLUEPRINT_IDENTIFIER, {
            'identifier': package_release_id,
            'title': package_release_id,
            "properties": {
                "Version": version
            },
            "relations": {
                "library": package_id
            }

        })
        packages_results.append(package_release_id)
    return packages_results
