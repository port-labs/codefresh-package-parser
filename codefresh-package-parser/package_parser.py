from utils import normalize_identifier
from port import get_port_entity, upsert_port_entity
import xmltodict


PACKAGE_BLUEPRINT_IDENTIFIER = 'library'
PACKAGE_RELEASE_BLUEPRINT_IDENTIFIER = 'library-release'


def parse_packages_based_on_manager_type(port_access_token, package_manager_type, package_file_content, packages_filter):
    if package_manager_type == 'C_SHARP_PROJECT':
        return parse_packages_from_c_sharp_proj(port_access_token, package_file_content, packages_filter)
    elif package_manager_type == 'NPM':
        return {}


def parse_packages_from_c_sharp_proj(port_access_token, package_file_content, packages_filter):
    packages_results = []
    project_structure_dict = xmltodict.parse(package_file_content)
    item_groups_array = project_structure_dict['Project']['ItemGroup']

    for item_group in item_groups_array:
        if 'PackageReference' in item_group:
            packages_array = item_group['PackageReference']
            packages_results = packages_results + parse_packages_from_c_sharp_item_group(
                port_access_token, packages_array, packages_filter)

    return packages_results


def parse_packages_from_c_sharp_item_group(port_access_token, packages_array, packages_filter: str):
    packages_results = []
    for package_reference in packages_array:
        if packages_filter.lower() in package_reference['@Include'].lower():
            package_id = normalize_identifier(package_reference['@Include'])
            upsert_port_entity(port_access_token, PACKAGE_BLUEPRINT_IDENTIFIER, {
                'identifier': package_id,
                'title': package_id,
                "properties": {}
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
