"""
Глобальные фикстуры для тестов J02-free-limited.

Определены на уровне tests/ для видимости всеми тестовыми файлами.
"""

import pytest
from tests.helpers.api_stub import ZvukFreeApiStub


@pytest.fixture(scope="function")
def api_client() -> ZvukFreeApiStub:
    """Фикстура, возвращающая экземпляр API-заглушки.

    Перед каждым тестом создаётся новый экземпляр Stub с чистым состоянием.
    """
    return ZvukFreeApiStub()


@pytest.fixture(scope="function")
def free_authenticated_client(api_client: ZvukFreeApiStub) -> ZvukFreeApiStub:
    """Фикстура, возвращающая API-клиент с уже прошедшей регистрацией (Free).

    Выполняет:
      1. Отправка СМС-кода на номер +7 999 000-00-22
      2. Подтверждение кода 111222
      3. Вход выполнен — пользователь авторизован как Free
    """
    api_client.send_sms_code("+7 999 000-00-22")
    api_client.confirm_sms_code("+7 999 000-00-22", "111222")
    return api_client