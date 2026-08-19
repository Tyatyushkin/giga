"""
Глобальные фикстуры для journey J01-purchase-flow.

Фикстура api_client создаёт свежий экземпляр KuperApiStub для каждого теста,
что обеспечивает изоляцию шагов одного теста и независимость тестов друг от друга.
"""

from __future__ import annotations

import pytest

from api_stub import KuperApiStub


@pytest.fixture
def api_client() -> KuperApiStub:
    """Свежий экземпляр API-стаба для каждого теста."""
    return KuperApiStub()
