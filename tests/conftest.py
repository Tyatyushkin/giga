"""
E2E Test Case Factory — корневой conftest

Предоставляет глобальные фикстуры для всех тестов.
"""

import pytest
from pathlib import Path

# Корень проекта — для построения путей к тестовым артефактам
PROJECT_ROOT = Path(__file__).parent.parent


@pytest.fixture(scope="session")
def project_root() -> Path:
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def output_cases_root() -> Path:
    """Путь к каталогу с кейсами (для валидации)."""
    return PROJECT_ROOT / "output" / "cases"


@pytest.fixture(scope="session")
def output_report_root() -> Path:
    return PROJECT_ROOT / "output" / "report.md"