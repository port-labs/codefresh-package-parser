import sys
from git import Repo
from pathlib import Path

import logging

logger = logging.getLogger('package_parser.git_client')


TOKEN_AUTH_HEADER = 'x-token-auth'


def clone_repo_and_map_files(repo_url, access_token, PACKAGES_FILE_FILTER):
    logger.info(f'Cloning from repo {repo_url}')
    repo = clone_target_repo(repo_url, access_token)
    logger.info(f'Repo cloned')
    file_path_list = []
    for path in Path('./tmp').rglob(PACKAGES_FILE_FILTER):
        file_path_list.append(path)
        logger.info(path)
    return file_path_list


def clone_target_repo(repo_url, access_token):
    # for example https://x-token-auth:aaaaaaaa@bitbucket.org/workspace/repo-name.git
    try:
        return Repo.clone_from(f'https://{TOKEN_AUTH_HEADER}:{access_token}@{repo_url}', './tmp')
    except Exception as err:
        logger.error(f'Repository cloned failed: {err}')
