from toolbox.utils.test_utils import RequestHelper, check_status_code

request = RequestHelper(default_host="akta-wikipopa.hack4krak.pl")


def test_index_page_loads():
    response = request.get("/")

    check_status_code(response, 200)

    assert "text/html" in response.headers.get("Content-Type", "")
    assert len(response.text) > 0
