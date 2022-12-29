from git import Repo

import logging

logger = logging.getLogger('git_client')

TOKEN_AUTH_HEADER = 'x-token-auth'


def get_file_contents(repo_url, access_token, target_file_path):
    logger.info(f'Cloning from repo {repo_url}')
    repo = clone_target_repo(repo_url, access_token)
    # GitPython offers a convenience method that allows you to use POSIX-like paths from the repo tree towards files in the repository
    target_file = repo.tree() / target_file_path
    target_contents = target_file.data_stream.read().decode()
    logger.info(f'Repo cloned')
    return target_contents


def clone_target_repo(repo_url, access_token):
    # for example https://x-token-auth:aaaaaaaa@bitbucket.org/workspace/repo-name.git
    try:
        return Repo.clone_from(f'https://{TOKEN_AUTH_HEADER}:{access_token}@{repo_url}', './tmp')
    except Exception as err:
        logger.error(f'Repository cloned failed: {err}')
