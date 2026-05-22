from pathlib import Path

import requests

from toolbox.utils.test_utils import RequestHelper, check_flag_in_response, check_status_code, load_flag_hash

ARCHIVE_HOST = "https://archiwum31.norbiros.dev"
COMMIT_URL = "https://github.com/CrabCraftDev/CrabNBT/commit/f226853a9f45d63559e433bc42f57be64b64646b"

request = RequestHelper(base_url=ARCHIVE_HOST)
task_path = Path(__file__).parent.parent


def test_archive_site_loads():
    response = request.get("/")
    check_status_code(response, 200)


def test_solution_commit_contains_flag():
    response = requests.get(COMMIT_URL, timeout=10.0)
    check_status_code(response, 200)

    flag_hash = load_flag_hash(task_path)
    assert flag_hash is not None
    check_flag_in_response(response, flag_hash)
