import sys
from git import Repo
from pathlib import Path

import logging

logger = logging.getLogger('package_parser.git_client')


def clone_repo_and_map_files(repo_url, username, app_password, PACKAGES_FILE_FILTER):
    logger.info(f'Cloning from repo {repo_url}')
    repo = clone_target_repo(repo_url, username, app_password)
    logger.info(f'Repo cloned')
    file_path_list = []
    for path in Path('./tmp').rglob(PACKAGES_FILE_FILTER):
        file_path_list.append(path)
        logger.info(path)
    return file_path_list


def clone_target_repo(repo_url, username, app_password):
    # for example git clone https://{bitbucket_username}:{app_password}@bitbucket.org/{workspace}/{repository}.git
    try:
        return Repo.clone_from(f'https://{username}:{app_password}@{repo_url}', './tmp')
    except Exception as err:
        logger.error(f'Repository clone failed: {err}')
