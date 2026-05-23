import os
import re
import time
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor

import pytest
import requests

from toolbox.utils.test_utils import check_status_code

TASK_HOST = "smog4shell.hack4krak.pl"
SOLR_PATH = "/solr/admin/info/system"
SOLR_RETRIES = 18
SOLR_RETRY_DELAY = 5
PARALLEL_CREATE_REQUESTS = 4


def _url(path: str) -> str:
    base_url = os.getenv("TASKS_DEPLOYMENT_URL", "http://localhost:8000")
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


@pytest.fixture()
def client() -> Iterator[requests.Session]:
    session = requests.Session()

    response = None
    for _ in range(12):
        response = session.post(_url("/api/login"), headers={"Host": TASK_HOST}, timeout=5)
        if response.status_code == 200:
            break
        if response.status_code == 404:
            break
        print(f"POST /api/login -> {response.status_code} {response.text[:120]!r}", flush=True)
        time.sleep(5)

    assert response is not None
    check_status_code(response)
    assert response.json() == {"ok": True}
    assert "session" in session.cookies

    try:
        yield session
    finally:
        _release_instance(session)


def _create_instance(session: requests.Session) -> str:
    print("POST /api/create", flush=True)
    response = session.post(_url("/api/create"), headers={"Host": TASK_HOST}, timeout=5)
    print(f"POST /api/create -> {response.status_code} {response.text[:200]}", flush=True)
    check_status_code(response)

    url = response.json().get("url")
    assert re.fullmatch(r"[a-f0-9]{8}-solr\.hack4krak\.pl", url), response.text
    return url


def _release_instance(session: requests.Session) -> None:
    response = session.post(_url("/api/release"), headers={"Host": TASK_HOST}, timeout=30)
    check_status_code(response)
    assert response.json() == {"ok": True}


def _wait_for_solr(host: str) -> str:
    last_response = None

    for _ in range(SOLR_RETRIES):
        try:
            print(f"GET {host}{SOLR_PATH}", flush=True)
            response = requests.get(_url(SOLR_PATH), headers={"Host": host}, timeout=5)
            print(f"GET {host}{SOLR_PATH} -> {response.status_code} {response.text[:120]!r}", flush=True)
            if response.status_code == 200 and "lucene" in response.text.lower():
                return response.text
            if response.status_code == 404:
                pytest.fail(f"Solr endpoint returned 404, aborting early: {response.text[:300]}")
            last_response = response
        except requests.RequestException:
            pass

        time.sleep(SOLR_RETRY_DELAY)

    if last_response is not None:
        pytest.fail(
            f"Solr did not become ready, last status={last_response.status_code}, body={last_response.text[:300]}"
        )
    raise AssertionError("Solr did not become ready")


def _check_solr_query(host: str) -> None:
    payload = "${jndi:ldap://127.0.0.1:1389/Exploit}"
    response = requests.get(
        _url(f"/solr/admin/cores?cokolwiek={payload}"),
        headers={"Host": host},
        timeout=10,
    )
    assert response.status_code != 404, response.text[:300]


@pytest.mark.timeout(180)
def test_full_path_creates_instance_and_exposes_solr(client: requests.Session) -> None:
    instance_host = _create_instance(client)

    try:
        body = _wait_for_solr(instance_host)
        assert "lucene" in body.lower()

        _check_solr_query(instance_host)
    finally:
        _release_instance(client)


@pytest.mark.timeout(180)
def test_repeated_and_parallel_creates_reuse_one_instance(client: requests.Session) -> None:
    first_url = _create_instance(client)

    try:
        second_url = _create_instance(client)
        assert second_url == first_url

        with ThreadPoolExecutor(max_workers=PARALLEL_CREATE_REQUESTS) as executor:
            urls = list(executor.map(lambda _: _create_instance(client), range(PARALLEL_CREATE_REQUESTS)))

        assert set(urls) == {first_url}
    finally:
        _release_instance(client)
