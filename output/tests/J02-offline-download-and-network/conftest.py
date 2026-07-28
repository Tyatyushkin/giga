"""
Глобальные фикстуры для тестового пакета J02-offline-download-and-network.

Предоставляет:
- api_client — сконфигурированный HTTP-клиент (заглушка)
- authenticated_client — клиент с активной подпиской Premium
- unauthenticated_client — клиент без подписки (Free-тариф)
- network_stable — фикстура стабильного сетевого соединения
- network_unstable — фикстура с имитацией обрыва сети
"""

import pytest


@pytest.fixture(scope="function")
def api_client():
    """
    Возвращает экземпляр эмулированного API-клиента
    (ApiStub) с детерминированным поведением.
    """
    from api_stub import ApiStub

    return ApiStub()


@pytest.fixture(scope="function")
def authenticated_client(api_client):
    """
    Клиент с активной платной подпиской Premium.

    Наследует api_client + pre-устанавливает:
    - subscription = "premium"
    - is_authenticated = True
    - play_queue = ["Весна — Дельфин"]
    - collection = ["Весна — Дельфин", "Голос — Дельфин"]
    """
    api_client._set_subscription("premium")
    api_client._set_authenticated(True)
    api_client._set_play_queue(
        ["Весна — Дельфин", "Голос — Дельфин"]
    )
    return api_client


@pytest.fixture(scope="function")
def unauthenticated_client(api_client):
    """
    Клиент без активной подписки (Free-тариф).

    Наследует api_client + pre-устанавливает:
    - subscription = None / "free"
    - is_authenticated = True (но подписка отсутствует)
    """
    api_client._set_subscription(None)
    api_client._set_authenticated(True)
    api_client._set_play_queue([])
    return api_client


@pytest.fixture(scope="function")
def network_stable():
    """
    Стабильное сетевое соединение.
    Возвращает True — сеть доступна.
    """
    return True


@pytest.fixture(scope="function")
def network_unstable():
    """
    Нестабильное сетевое соединение (обрыв).

    Возвращает False — сеть недоступна.
    """
    return False