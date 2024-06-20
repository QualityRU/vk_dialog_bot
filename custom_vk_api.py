import linecache
import random
import re

import requests
import vk_api
from dotenv import dotenv_values
from fake_useragent import UserAgent

# Загрузка конфигурационных данных из файла .env
config = dotenv_values('.env')
ua = UserAgent()
PROXY_FILE: str = config['PROXY_FILE']
# USER_AGENT: str = config[
#     'USER_AGENT'
# ]  # Пользовательский агент для HTTP-запросов
USER_AGENT: str = ua.random


def validate_proxy(proxy):
    pattern = r'^([^:@]+):([^@]+)@([^:]+):(\d+)$'
    match = re.match(pattern, proxy)
    if match:
        return True
    return False


def get_random_proxy(file_path):
    try:
        num_lines = sum(1 for line in open(file_path))
        print('Запуск с рандомным прокси...')
        random_line_number = random.randint(1, num_lines)
        random_proxy = linecache.getline(file_path, random_line_number).strip()
    except Exception as e:
        print('Запуск без прокси...', e)
        return False

    # return validate_proxy(random_proxy)
    return random_proxy


class Custom_VkApi(vk_api.VkApi):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.http = requests.Session()
        self.http.headers[
            'User-agent'
        ] = USER_AGENT  # Установка пользовательского агента для запросов

        proxy = get_random_proxy(PROXY_FILE)

        if proxy:
            # http://{proxy_username}:{proxy_password}@{proxy_ip}:{proxy_port}
            # username:password@ip:port
            proxy_url = f'http://{proxy}'
            proxies = {'http': proxy_url, 'https': proxy_url}
            self.http.proxies.update(proxies)
