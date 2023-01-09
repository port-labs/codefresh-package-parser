from app.consts import API_URL, USER_AGENT, MAX_THREADS, CLIENT_ID_KEY, CLIENT_SECRET_KEY, ACCESS_TOKEN_KEY
import requests
import logging
import threading

sema = threading.Semaphore(MAX_THREADS)

logger = logging.getLogger('package_parser.port_client')


def get_access_token(CLIENT_ID, CLIENT_SECRET):
    try:
        credentials = {CLIENT_ID_KEY: CLIENT_ID, CLIENT_SECRET_KEY: CLIENT_SECRET}
        token_response = requests.post(f'{API_URL}/auth/access_token', json=credentials)
        logger.info('Received access token from Port API')
        return token_response.json()[ACCESS_TOKEN_KEY]
    except Exception as err:
        logger.error('Failed to get access token')


def construct_headers(access_token):
    return {
        'Authorization': f'Bearer {access_token}',
        'User-Agent': USER_AGENT
    }


def get_port_entity(port_credentials, blueprint_id, entity_id):
    headers = construct_headers(access_token=port_credentials[ACCESS_TOKEN_KEY])
    res = requests.get(f'{API_URL}/blueprints/{blueprint_id}/entities/{entity_id}', headers=headers)
    if res.status_code == 200:
        return res.json()

    logger.error(f'Entity {entity_id} not found')
    return None


def upsert_port_entity(port_credentials, blueprint_id, body):
    headers = construct_headers(access_token=port_credentials[ACCESS_TOKEN_KEY])
    sema.acquire()
    res = requests.post(f'{API_URL}/blueprints/{blueprint_id}/entities?upsert=true&merge=true', headers=headers, json=body)
    sema.release()
    if res.status_code == 200 or res.status_code == 201:
        logger.info(f'Finished Creating {blueprint_id}: {body["identifier"]}')
        return res.json()

    if res.status_code == 401 and res.json()['error'] == 'JwtParseError':
        logger.info(f'JWT expired, getting new token and retrying')
        port_credentials[ACCESS_TOKEN_KEY] = get_access_token(port_credentials[CLIENT_ID_KEY, CLIENT_SECRET_KEY])
        headers = construct_headers(access_token=port_credentials[ACCESS_TOKEN_KEY])
        sema.acquire()
        res = requests.post(f'{API_URL}/blueprints/{blueprint_id}/entities?upsert=true&merge=true', headers=headers, json=body)
        sema.release()
        if res.status_code == 200 or res.status_code == 201:
            return res.json()

    logger.error(f'Entity {body["identifier"]} not created')
    # logger.error(f'Error: {res.json().get("error", None)}')
    # logger.error(f'Message: {res.json().get("message", None)}')
    logger.error(f'Complete response: {res.json()}')
    return None
