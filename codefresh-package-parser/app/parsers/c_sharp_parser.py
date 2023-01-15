from app.parsers.utils import report_library_releases, construct_library_body, construct_library_release_body
from app.utils import normalize_package_filters, normalize_identifier
from app.port import upsert_port_entity, get_all_blueprint_entities
import logging
import xmltodict
from app.consts import PACKAGE_RELEASE_BLUEPRINT_IDENTIFIER, PACKAGE_BLUEPRINT_IDENTIFIER
import threading


logger = logging.getLogger('packageparser.parser.c_sharp')


def parse_packages_from_c_sharp_package_files(port_credentials, package_file_path_list, package_filters):
    packages_results = []
    normalized_filters = normalize_package_filters(package_filters.split(','))
    logger.info(f'Filters are: {normalized_filters}')
    for package_file_path in package_file_path_list:
        logger.info(f'Parsing packages from file: {package_file_path}')
        with open(package_file_path) as f:
            project_structure_dict = xmltodict.parse(f.read())
            packages_results = packages_results + parse_packages_from_c_sharp_proj(port_credentials, project_structure_dict, normalized_filters)
    return packages_results


def parse_packages_from_c_sharp_proj(port_credentials, project_structure_dict, package_filters):
    packages_results = []
    item_groups_array = project_structure_dict['Project']['ItemGroup']
    if isinstance(item_groups_array, dict):
        item_groups_array = [item_groups_array]
    for item_group in item_groups_array:
        if 'PackageReference' in item_group:
            packages_array = item_group['PackageReference']
            packages_results = packages_results + parse_packages_from_c_sharp_item_group(
                port_credentials, packages_array, package_filters)

    return packages_results


def parse_packages_from_c_sharp_item_group(port_credentials, packages_array, packages_filters: str):
    package_language = "C#"
    existing_packages = get_all_blueprint_entities(port_credentials, PACKAGE_BLUEPRINT_IDENTIFIER)
    existing_packages = [pkg['identifier'] for pkg in existing_packages]
    request_threads = []
    library_release_bodies = []
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
        body = construct_library_body(package_id, package_language, internal_package)
        if package_id not in existing_packages:
            logger.info(f'Creating library: {package_id}')
            req_thread = threading.Thread(target=upsert_port_entity, args=(port_credentials, PACKAGE_BLUEPRINT_IDENTIFIER, body))
            req_thread.start()
            request_threads.append(req_thread)
        else:
            logger.info(f'Skipping existing library: {package_id}')
        package_release_id = f'{package_id}_{normalize_identifier(package_reference["@Version"])}'
        logger.debug(f'Normalized release identifier: {package_release_id}')
        library_release_bodies.append(construct_library_release_body(package_release_id, package_reference["@Version"], package_id))
    for thread in request_threads:
        thread.join()
    return report_library_releases(port_credentials, library_release_bodies)
