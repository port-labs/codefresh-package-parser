import threading
from app.utils import normalize_package_filters, normalize_identifier
from app.port import upsert_port_entity, get_all_blueprint_entities
from app.parsers.utils import construct_library_body, construct_library_release_body, report_library_releases
import logging
import json
from app.consts import PACKAGE_RELEASE_BLUEPRINT_IDENTIFIER, PACKAGE_BLUEPRINT_IDENTIFIER


logger = logging.getLogger('packageparser.parser.npm')


def parse_packages_from_npm_package_files(port_credentials, package_file_path_list, package_filters):
    packages_results = []
    normalized_filters = normalize_package_filters(package_filters.split(','))
    logger.info(f'Filters are: {normalized_filters}')
    for package_file_path in package_file_path_list:
        logger.info(f'Parsing packages from file: {package_file_path}')
        with open(package_file_path) as f:
            project_structure_dict = json.load(f)
            packages_results = packages_results + parse_packages_from_package_json(port_credentials, project_structure_dict, normalized_filters)
    return packages_results


def parse_packages_from_package_json(port_credentials, project_structure_dict, package_filters):
    packages_results = []
    dependencies = project_structure_dict['dependencies']
    dev_dependencies = project_structure_dict['devDependencies']
    packages_results = packages_results + parse_packages_from_dependency_group(port_credentials, dependencies, package_filters)
    packages_results = packages_results + parse_packages_from_dependency_group(port_credentials, dev_dependencies, package_filters)

    return packages_results


def parse_packages_from_dependency_group(port_credentials, dependencies, packages_filters: str):
    package_language = "Node"
    existing_packages = get_all_blueprint_entities(port_credentials, PACKAGE_BLUEPRINT_IDENTIFIER)
    existing_packages = [pkg['identifier'] for pkg in existing_packages]
    request_threads = []
    library_release_bodies = []
    for package_name, version in dependencies.items():
        internal_package = False
        logger.debug(f'Looking at package: {package_name}')
        if any(filter in package_name.lower() for filter in packages_filters):
            internal_package = True
        logger.debug(f'Package {package_name} is internal: {internal_package}')
        package_id = normalize_identifier(package_name)
        logger.debug(f'Normalized package identifier: {package_id}')
        body = construct_library_body(package_id, package_language, internal_package)
        if package_id not in existing_packages:
            logger.info(f'Creating library: {package_id}')
            req_thread = threading.Thread(target=upsert_port_entity, args=(port_credentials, PACKAGE_BLUEPRINT_IDENTIFIER, body))
            req_thread.start()
            request_threads.append(req_thread)
        else:
            logger.info(f'Skipping existing library: {package_id}')
        package_release_id = f'{package_id}_{normalize_identifier(version)}'
        logger.debug(f'Normalized release identifier: {package_release_id}')
        library_release_bodies.append(construct_library_release_body(package_release_id, version, package_id))

    for thread in request_threads:
        thread.join()
    return report_library_releases(port_credentials, library_release_bodies)
