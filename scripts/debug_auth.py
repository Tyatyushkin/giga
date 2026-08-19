#!/usr/bin/env python3
"""Отладка аутентификации."""
import sys
sys.path.insert(0, "output/tests/j01-knox-demo-topology-lifecycle")

from api_stub_j01 import _check_basic_auth, reset_state, route_request, StubRequest
from data_j01 import ADMIN_AUTH_HEADER, TOPOLOGY_XML, TOPOLOGY_NAME, BASE_URL
import base64

print(f"ADMIN_AUTH_HEADER = {ADMIN_AUTH_HEADER}")

# Проверим, как работает _check_basic_auth с этим хедером
auth_val = ADMIN_AUTH_HEADER["Authorization"]
print(f"\nAuth header value: {auth_val}")
print(f"Starts with 'Basic ': {auth_val.startswith('Basic ')}")
token_part = auth_val[6:]
print(f"Token part (after 'Basic '): {token_part}")

try:
    decoded = base64.b64decode(token_part).decode("utf-8")
    print(f"Decoded (b64): {decoded}")
    user, pwd = decoded.split(":", 1)
    print(f"User: {user}, Pass: {pwd}")
except Exception as e:
    print(f"b64 decode failed: {e}")

print(f"\n_check_basic_auth result: {_check_basic_auth(auth_val)}")

# Попробуем напрямую вызвать маршрут
reset_state()
print(f"\n=== Route test ===")
req = StubRequest("PUT", f"/gateway/admin/api/v1/topologies/{TOPOLOGY_NAME}", ADMIN_AUTH_HEADER, TOPOLOGY_XML)
resp = route_request(req)
print(f"Direct route: status={resp.status}")

# Попробуем через api_client (conftest)
from conftest import api_client
fixture = api_client(None)  # вызываем как функцию-фикстуру
reset_state()
url = f"{BASE_URL}/gateway/admin/api/v1/topologies/{TOPOLOGY_NAME}"
print(f"\nURL passed to client: {url}")
resp2 = fixture.request("PUT", url, headers=ADMIN_AUTH_HEADER, body=TOPOLOGY_XML)
print(f"Via client: status={resp2.status}")
