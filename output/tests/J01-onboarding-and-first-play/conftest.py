"""
Глобальные фикстуры для тестов J01-onboarding-and-first-play.
"""

import pytest
from api_stub import ZvukApiStub


@pytest.fixture(scope="function")
def api_client():
    """Фикстура, возвращающая экземпляр API-заглушки.

    Перед каждым тестом создаётся новый экземпляр Stub с чистым состоянием.
    """
    return ZvukApiStub()


@pytest.fixture(scope="function")
def authenticated_client(api_client: ZvukApiStub) -> ZvukApiStub:
    """Фикстура, возвращающая API-клиент с уже прошедшей регистрацией.

    Выполняет последовательность:
      1. Отправка кода на номер +7 999 000-00-11
      2. Подтверждение кода 1111
      3. Выбор жанров Электроника, Хип-хоп, Инди
      4. Подтверждение онбординга
    """
    api_client.send_code("+7 999 000-00-11")
    api_client.confirm_code("+7 999 000-00-11", "1111")
    api_client.select_genres(["Электроника", "Хип-хоп", "Инди"])
    api_client.confirm_onboarding()
    return api_client