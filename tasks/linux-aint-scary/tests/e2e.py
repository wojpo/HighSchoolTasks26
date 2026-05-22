from toolbox.utils.test_utils import RequestHelper, check_status_code

request = RequestHelper(default_host="linux-aint-scary.hack4krak.pl")


def _find_first_hash(entries: list) -> str:
    for entry in entries:
        if len(entry) == 7 and isinstance(entry[6], str):
            return entry[6]
        if len(entry) == 7 and isinstance(entry[6], list):
            result = _find_first_hash(entry[6])
            if result:
                return result
    return ""


def test_static_page_served():
    response = request.get("/")
    check_status_code(response, 200)


def test_v86_assets_served():
    response = request.get("/v86/build/libv86.js")
    check_status_code(response, 200)

    response = request.get("/v86/build/v86.wasm")
    check_status_code(response, 200)


def test_bios_images_served():
    response = request.get("/v86/bios/seabios.bin")
    check_status_code(response, 200)

    response = request.get("/v86/bios/vgabios.bin")
    check_status_code(response, 200)


def test_rootfs_images_served():
    fs_response = request.get("/images/alpine-fs.json")
    check_status_code(fs_response, 200)

    response = request.get("/images/v86state.bin")
    check_status_code(response, 200)

    hash_name = _find_first_hash(fs_response.json()["fsroot"])
    assert hash_name, "No file hash found in alpine-fs.json"
    response = request.get(f"/images/alpine-rootfs-flat/{hash_name}")
    check_status_code(response, 200)
