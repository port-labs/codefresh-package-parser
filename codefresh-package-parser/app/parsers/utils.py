import threading

from app.consts import PACKAGE_RELEASE_BLUEPRINT_IDENTIFIER

from app.port import upsert_port_entity


def construct_library_body(package_id, package_language, internal_package):
    return {
        'identifier': package_id,
        'title': package_id,
        "properties": {
            "Language": package_language,
            "Internal": internal_package
        }
    }


def construct_library_release_body(package_release_id, version, package_id):
    return {
        'identifier': package_release_id,
        'title': package_release_id,
        "properties": {
            "Version": version
        },
        "relations": {
            "library": package_id
        }
    }


def report_library_releases(port_credentials, library_release_bodies):
    packages_results = []
    request_threads = []
    for library_release in library_release_bodies:
        req_thread = threading.Thread(target=upsert_port_entity, args=(port_credentials, PACKAGE_RELEASE_BLUEPRINT_IDENTIFIER, library_release))
        req_thread.start()
        request_threads.append(req_thread)
        packages_results.append(library_release['identifier'])
    for thread in request_threads:
        thread.join()
    return packages_results
