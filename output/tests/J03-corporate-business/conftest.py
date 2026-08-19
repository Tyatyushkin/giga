"""
Глобальные фикстуры для journey J03-corporate-business.

Фикстура api_client создаёт свежий экземпляр CorporateApiStub для каждого теста,
что обеспечивает изоляцию шагов одного теста и независимость тестов друг от друга.
"""

from __future__ import annotations

import pytest

from api_stub import CorporateApiStub


@pytest.fixture
def api_client() -> CorporateApiStub:
    """Свежий экземпляр API-стаба для каждого теста."""
    return CorporateApiStub()
