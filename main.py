from pprint import pprint
from typing import Optional, Tuple

import vk_api
from dotenv import dotenv_values
from vk_api.longpoll import VkEventType, VkLongPoll

from custom_vk_api import Custom_VkApi

# Загрузка конфигурационных данных из файла .env
config = dotenv_values('.env')
APP_ID: int = config['APP_ID']  # ID приложения ВКонтакте
TOKEN: str = config['TOKEN']  # Токен для доступа к API
LOGIN: str = config['LOGIN']  # Логин пользователя
PASSWORD: str = config['PASSWORD']  # Пароль пользователя


def auth_handler() -> Tuple[str, bool]:
    """Функция для обработки двухфакторной аутентификации"""
    key = input('Введите код двухфакторной аутентификации: ')
    remember_device = True  # Запомнить устройство
    return key, remember_device


def captcha_handler() -> Optional[str]:
    """Функция для обработки капчи"""
    return None


def vk_msg_send(
    session: vk_api.vk_api.VkApiMethod,
    user_id: int,
    message: str,
    random_id: int,
) -> None:
    """Отправка сообщения пользователю ВКонтакте"""
    try:
        session.messages.send(
            user_id=user_id,
            message=message,
            random_id=random_id,
        )
    except vk_api.ApiError as error_msg:
        if error_msg.code == 17:
            validation_url = error_msg.error['redirect_uri']
            print(
                f'Пожалуйста, откройте этот URL-адрес в браузере для проверки: {validation_url}'
            )
        else:
            print(error_msg)


def main() -> None:
    vk_session = Custom_VkApi(
        app_id=APP_ID,
        login=LOGIN,
        password=PASSWORD,
        auth_handler=auth_handler,
        # captcha_handler=captcha_handler,
    )

    try:
        vk_session.auth(token_only=True)
    except vk_api.Captcha as captcha:
        captcha_image_url = captcha.get_url()
        print(f'Пожалуйста, решите эту проблему с капчей: {captcha_image_url}')
        captcha_key = input('Введите текст капчи: ')
        captcha.try_again(captcha_key)
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    print('Бот запущен и готов к работе...')

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            # user_id = event.user_id
            user_id = event.peer_id
            print(event.raw)
            print(f'Новое сообщение от {user_id}: {event.text}')
            if event.text == 'start':
                vk_msg_send(
                    session=vk,
                    user_id=user_id,
                    message='Ваш ответ на нажатие кнопки',
                    random_id=0,
                )

            # Проверка наличия кнопок в сообщении
            if 'payload' in event.raw[6]:
                payload = event.raw[6]['payload']
                print(f'Получен payload: {payload}')

                # Пример обработки payload
                if payload == 'some_payload_value':
                    vk_msg_send(
                        session=vk,
                        user_id=event.user_id,
                        message='Ваш ответ на нажатие кнопки',
                        random_id=0,
                    )


if __name__ == '__main__':
    main()
