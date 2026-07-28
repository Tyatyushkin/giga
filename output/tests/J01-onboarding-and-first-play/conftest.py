"""
conftest.py — global fixtures for J01-onboarding-and-first-play tests.

Provides a function-scoped ``api_client`` fixture that yields a clean
``ZvukAPIClient`` instance for every test function.
"""

from __future__ import annotations

import pytest

from api_stub import ZvukAPIClient


@pytest.fixture(scope="function")
def api_client() -> ZvukAPIClient:
    """
    Return a fresh, reset ZvukAPIClient instance.

    Every test receives its own client with clean internal state:
    - no phone registered
    - not authenticated
    - no genres selected
    - no current track / queue
    """
    client = ZvukAPIClient()
    client.reset()
    return client


@pytest.fixture(scope="function")
def authenticated_client(api_client: ZvukAPIClient) -> ZvukAPIClient:
    """
    Return a ZvukAPIClient that has already completed
    phone → SMS → confirmation → authentication flow.

    This fixture is a convenience for tests that start after
    authentication (e.g. TC-J01-03, TC-J01-04).
    """
    from test_data import TC_J01_00_Data

    api_client.send_confirmation_code(TC_J01_00_Data.PHONE)
    api_client.confirm_code(TC_J01_00_Data.CONFIRMATION_CODE)
    return api_client


@pytest.fixture(scope="function")
def onboarded_client(authenticated_client: ZvukAPIClient) -> ZvukAPIClient:
    """
    Return a client that has completed the full onboarding:
    authenticated + 3 genres selected.

    This fixture is a convenience for tests that start after
    the main screen is shown (e.g. TC-J01-04).
    """
    from test_data import TC_J01_00_Data

    authenticated_client.select_genres(list(TC_J01_00_Data.GENRES))
    return authenticated_client