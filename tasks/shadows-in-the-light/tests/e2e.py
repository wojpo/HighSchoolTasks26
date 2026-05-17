from toolbox.utils.test_utils import RequestHelper, check_status_code, check_text_contains

HOST = "shadows-in-the-light.hack4krak.pl"
IMAGE_PATHS = [
    "images/kaplica-poranna.webp",
    "images/kaplica-poranna-bigger-preview.png",
    "images/wyspianski-zlota-brama.webp",
    "images/wyspianski-zlota-brama-preview.webp",
]


def test_home_page_loads() -> None:
    response = RequestHelper(default_host=HOST).get("/")

    check_status_code(response)
    for image in IMAGE_PATHS:
        check_text_contains(response, image)


def test_all_picture_sources_return_valid_images() -> None:
    helper = RequestHelper(default_host=HOST)

    for path in IMAGE_PATHS:
        response = helper.get(path)
        check_status_code(response)
