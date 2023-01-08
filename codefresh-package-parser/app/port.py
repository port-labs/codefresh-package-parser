import sys
from app.consts import API_URL, USER_AGENT, MAX_THREADS
import requests
import logging

logger = logging.getLogger('package_parser.port_client')


def get_access_token(CLIENT_ID, CLIENT_SECRET):
    try:
        credentials = {'clientId': CLIENT_ID, 'clientSecret': CLIENT_SECRET}
        token_response = requests.post(f'{API_URL}/auth/access_token', json=credentials)
        logger.info('Received access token from Port API')
        return token_response.json()['accessToken']
    except Exception as err:
        logger.error('Failed to get access token')


def construct_headers(access_token):
    return {
        'Authorization': f'Bearer {access_token}',
        'User-Agent': USER_AGENT
    }


def get_port_entity(access_token, blueprint_id, entity_id):
    headers = construct_headers(access_token=access_token)
    res = requests.get(f'{API_URL}/blueprints/{blueprint_id}/entities/{entity_id}', headers=headers)
    if res.status_code == 200:
        return res.json()

    logger.error(f'Entity {entity_id} not found')
    return None


def upsert_port_entity(access_token, blueprint_id, body):
    headers = construct_headers(access_token=access_token)
    res = requests.post(f'{API_URL}/blueprints/{blueprint_id}/entities?upsert=true&merge=true', headers=headers, json=body)
    if res.status_code == 200 or res.status_code == 201:
        return res.json()

    logger.error(f'Entity {body["identifier"]} not created')
    logger.error(f'Error: {res.json().get("error", None)}')
    logger.error(f'Message: {res.json().get("message", None)}')
    logger.error(f'Complete response: {res.json()}')
    return None
