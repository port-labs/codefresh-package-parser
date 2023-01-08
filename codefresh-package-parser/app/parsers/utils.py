from port import get_port_entity


def check_if_package_exists_in_port(port_access_token, blueprint_identifier, package_identifier):
    if get_port_entity(port_access_token, blueprint_identifier, package_identifier):
        return True
    return False
