from git import Repo

import logging

logger = logging.getLogger('git_client')

TOKEN_AUTH_HEADER = 'x-token-auth'


def get_file_contents(repo_url, access_token, target_file_path):
    logger.info(f'Cloning from repo {repo_url}')
    repo = clone_target_repo(repo_url, access_token)
    target_file = repo.tree() / target_file_path
    target_contents = target_file.data_stream.read().decode()
    return target_contents


def clone_target_repo(repo_url, access_token):
    # for example https://x-token-auth:aaaaaaaa@bitbucket.org/workspace/repo-name.git
    return Repo.clone_from(f'https://{TOKEN_AUTH_HEADER}:{access_token}@{repo_url}', './tmp')
