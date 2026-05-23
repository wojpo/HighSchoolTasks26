import re
from pathlib import Path

from toolbox.utils.test_utils import (
    RequestHelper,
    check_status_code,
    check_text_contains,
    load_flag_hash,
    validate_flag_hash,
)

request = RequestHelper(default_host="bibliotheca-jagellonica.hack4krak.pl")
task_path = Path(__file__).parent.parent

BACON = {
    "AAAAA": "A",
    "AAAAB": "B",
    "AAABA": "C",
    "AAABB": "D",
    "AABAA": "E",
    "AABAB": "F",
    "AABBA": "G",
    "AABBB": "H",
    "ABAAA": "I",
    "ABAAB": "K",
    "ABABA": "L",
    "ABABB": "M",
    "ABBAA": "N",
    "ABBAB": "O",
    "ABBBA": "P",
    "ABBBB": "Q",
    "BAAAA": "R",
    "BAAAB": "S",
    "BAABA": "T",
    "BAABB": "U",
    "BABAA": "W",
    "BABAB": "X",
    "BABBA": "Y",
    "BABBB": "Z",
}


def test_home_page_loads() -> None:
    response = request.get("/")

    check_status_code(response)
    check_text_contains(response, "Bibliotheca Jagellonica")
    check_text_contains(response, "/catalog")


def test_robots_txt_blocks_crawlers() -> None:
    response = request.get("/robots.txt")

    check_status_code(response)
    check_text_contains(response, "User-agent: GPTBot")
    check_text_contains(response, "User-agent: ClaudeBot")
    check_text_contains(response, "Disallow: /")
    assert "noai" in response.headers["X-Robots-Tag"]


def test_known_ai_crawler_user_agents_are_blocked() -> None:
    response = request.get("/", headers={"User-Agent": "ClaudeBot/1.0"})

    check_status_code(response, 403)
    assert "noai" in response.headers["X-Robots-Tag"]


def test_catalog_lists_prolog_and_buffalo_but_not_lorem() -> None:
    response = request.get("/catalog")

    check_status_code(response)
    check_text_contains(response, "prolog.txt")
    check_text_contains(response, "buffalo.txt")
    assert "lorem.txt" not in response.text


def test_full_solution_path() -> None:
    """Solve the entire puzzle end-to-end, deriving every path from book content."""
    catalog = request.get("/catalog")
    check_status_code(catalog)

    buffalo_path = re.search(r"/library/[^\"' ]+/buffalo\.txt", catalog.text)
    assert buffalo_path, "buffalo.txt not found in catalog"
    buffalo_path = buffalo_path.group(0)

    resp = request.get(buffalo_path)
    check_status_code(resp)
    check_text_contains(resp, "Verulam wiedział, że alfabet może ukryć się")

    buffalo_lines = [
        line.strip()
        for line in resp.text.splitlines()
        if re.fullmatch(r"(buffalo|Buffalo)(\s+(buffalo|Buffalo)){4}", line.strip())
    ]
    assert len(buffalo_lines) == 5, f"Expected 5 Bacon-cipher lines, found {len(buffalo_lines)}"

    book_name = "".join(BACON["".join("B" if w[0].isupper() else "A" for w in line.split())] for line in buffalo_lines)
    assert book_name == "LOREM", f"Bacon decoded to {book_name!r}, expected 'LOREM'"

    lorem_path = buffalo_path.replace("buffalo.txt", f"{book_name.lower()}.txt")

    resp = request.get(lorem_path)
    check_status_code(resp)
    check_text_contains(resp, "Kanon:")
    check_text_contains(resp, "Odpis:")
    check_text_contains(resp, "Babel nie jest miejscem, lecz kluczem do obcego alfabetu")
    check_text_contains(resp, "zapieczętowana")

    kanon_match = re.search(r"Kanon:\n(.+)", resp.text)
    odpis_match = re.search(r"Odpis:\n(.+)", resp.text)
    assert kanon_match and odpis_match, "Kanon/Odpis not found in lorem.txt"

    kanon = kanon_match.group(1).strip()
    odpis = odpis_match.group(1).strip()

    changed = []
    for kw, ow in zip(kanon.split(), odpis.split(), strict=False):
        if kw != ow:
            first_diff = next((ow[i] for i in range(min(len(kw), len(ow))) if kw[i] != ow[i]), None)
            if first_diff and first_diff.isalpha():
                changed.append(first_diff)
    qi = "".join(changed).upper()
    assert qi == "QI", f"Expected 'QI' from kanon/odpis diff, got {qi!r}"

    vigenere_key = "BABEL"
    pi_name = "".join(
        chr((ord(c) - 65 - (ord(vigenere_key[i % len(vigenere_key)]) - 65)) % 26 + 65) for i, c in enumerate(qi)
    )
    assert pi_name == "PI", f"Vigenere(QI, BABEL) = {pi_name!r}, expected 'PI'"

    pi_path = lorem_path.replace("lorem.txt", f"{pi_name.lower()}.txt")

    cipher_path = re.search(
        r"/library/[^/\s`]+/wall/\d+/shelf/\d+/volume/\d+/book/cipher\.txt",
        resp.text,
    )
    assert cipher_path, "cipher.txt path not found in lorem.txt margin"
    cipher_path = cipher_path.group(0)

    resp = request.get(pi_path)
    check_status_code(resp)

    letters = "".join(c for c in resp.text if c.isalpha() and c.isupper())
    assert letters == "POLYGLOTLINGUAROMAE", f"Pi non-digit letters: {letters!r}"

    polyglot_path = pi_path.replace("pi.txt", "polyglot.txt")

    resp = request.get(polyglot_path, headers={"Accept-Language": "la"})
    check_status_code(resp)

    headers_path = re.search(
        r"/library/[^/\s`]+/wall/\d+/shelf/\d+/volume/\d+/book/headers\.txt",
        resp.text,
    )
    assert headers_path, "headers.txt path not found in polyglot.txt (latin response)"
    headers_path = headers_path.group(0)

    resp_plain = request.get(polyglot_path)
    check_status_code(resp_plain)
    assert "headers.txt" not in resp_plain.text, "headers.txt should be hidden without Accept-Language: la"

    resp = request.head(headers_path)
    check_status_code(resp)
    assert "Link" in resp.headers, "Link header missing from headers.txt response"

    link_match = re.search(r"<(/[^>]+)>", resp.headers["Link"])
    assert link_match, f"Could not parse Link header: {resp.headers['Link']!r}"
    final_path = link_match.group(1)
    assert "umbra.txt" in final_path

    resp = request.get(cipher_path)
    check_status_code(resp)
    check_text_contains(resp, "Zdejmij metaliczny atrament")
    check_text_contains(resp, "Klucz jest wspólny z tym, który otwierał obcy alfabet")
    assert "hack4KrakCTF" not in resp.text

    hex_match = re.search(r"[0-9a-f]{40,}", resp.text)
    assert hex_match, "No hex string found in cipher.txt"
    raw = bytes.fromhex(hex_match.group(0))
    key_bytes = b"babel"
    decoded = bytes([raw[i] ^ key_bytes[i % len(key_bytes)] for i in range(len(raw))]).decode("utf-8", errors="replace")

    assert "umbra.txt" in decoded, "Decrypted cipher does not reference umbra.txt"
    assert "13371337:13" in decoded, "Decrypted cipher missing BABEL fragment hint"

    resp = request.get(final_path)
    check_status_code(resp, 413)

    resp = request.get(final_path, headers={"Range": "bytes=-512"})
    check_status_code(resp, 206)
    check_text_contains(resp, "BABEL")

    fragment_map = {}
    for m in re.finditer(r"(\w+)\s+(\d+):(\d+)", resp.text):
        fragment_map[m.group(1)] = (int(m.group(2)), int(m.group(3)))

    assert set(fragment_map.keys()) >= {"BABEL", "E", "PI", "FI", "KRAKOW"}

    flag = ""
    for name in ["BABEL", "E", "PI", "FI", "KRAKOW"]:
        start, length = fragment_map[name]
        end = start + length - 1
        resp = request.get(final_path, headers={"Range": f"bytes={start}-{end}"})
        check_status_code(resp, 206)
        flag += resp.text

    m = re.fullmatch(r"hack4KrakCTF\{(.+)\}", flag)
    assert m is not None
    flag_hash = load_flag_hash(task_path)
    assert flag_hash is not None
    assert validate_flag_hash(m.group(1), flag_hash)
