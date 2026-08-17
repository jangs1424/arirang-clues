#!/usr/bin/env python3
"""rolebooks.json -> 롤북 QR 리다이렉트 페이지 / 카드에 넣을 QR 이미지.

QR 은 깃허브 페이지(/r/<코드>/)를 가리키고, 그 페이지가 노션 게시본으로 넘긴다.
노션 링크가 바뀌면 rolebooks.json 의 notion 값만 고치면 되고,
**인쇄한 QR 은 다시 만들 필요가 없다.** 단서카드 QR(/c/<코드>/)과 같은 구조다.
"""

import html
import json
import pathlib

import qrcode
from qrcode.constants import ERROR_CORRECT_Q

from build import GROUPS, BASE, qr_ink

ROOT = pathlib.Path(__file__).parent
DOCS = ROOT / "docs"
OUT = ROOT / "qr" / "rolebook"

# 카드에 얹을 PNG 해상도. A5 카드에서 QR 실물은 20mm 안쪽이라 box_size 16 이면
# 300dpi 인쇄에 충분하다. border=2 로 quiet zone 을 PNG 안에 넣는다 - 카드 배경이
# 어두워서 흰 여백이 이미지 밖에 있으면 스캔이 불안정해진다.
BOX_SIZE, BORDER = 16, 2

data = json.loads((ROOT / "rolebooks.json").read_text(encoding="utf-8"))
SITE = data["notionSite"].rstrip("/")
BOOKS = data["rolebooks"]

REDIRECT = """<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{en}</title>
<link rel="canonical" href="{target}">
<meta http-equiv="refresh" content="0;url={target}">
<meta name="robots" content="noindex">
<style>
  html,body{{margin:0;height:100%;background:#0b0b0c;color:#8a8a8a;
    display:flex;align-items:center;justify-content:center;text-align:center;
    font:14px/1.8 -apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo",sans-serif;}}
  a{{color:{color};}}
  b{{display:block;color:#ddd;letter-spacing:.08em;font-size:12px;margin-bottom:6px;}}
</style>
<script>location.replace("{target}");</script>
<div>
  <b>{en}</b>
  <a href="{target}">Open your rolebook</a>
</div>
"""


def target_url(code):
    """게시 주소는 슬러그 없이 ID 만 써도 열린다 - 노션이 제목 슬러그로 리다이렉트한다.
    제목을 고쳐도 주소가 깨지지 않으므로 ID 형태를 쓴다."""
    return f"{SITE}/{BOOKS[code]['notion']}"


def build_pages():
    for code, b in BOOKS.items():
        d = DOCS / "r" / code
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(
            REDIRECT.format(
                en=html.escape(b["en"]),
                target=target_url(code),
                color=GROUPS[code]["color"],
            ),
            encoding="utf-8",
        )


def build_index():
    rows = "".join(
        f'<li style="border-left:6px solid {GROUPS[c]["color"]}">'
        f'<a href="{c}/">{c}</a> {html.escape(GROUPS[c]["kr"])}'
        f'<span>{html.escape(b["en"])}</span></li>'
        for c, b in BOOKS.items()
    )
    (DOCS / "r" / "index.html").write_text(
        f"""<!doctype html>
<html lang="ko">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>아리랑마을 롤북 (영문)</title>
<style>
  body{{max-width:620px;margin:0 auto;padding:24px;
    font:15px/1.7 -apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo",sans-serif;color:#222;}}
  h1{{font-size:20px;}}
  p{{color:#666;font-size:13px;}}
  ul{{list-style:none;padding:0;}}
  li{{padding:6px 0 6px 10px;margin-bottom:6px;}}
  a{{color:#0645ad;font-weight:700;}}
  span{{display:block;color:#888;font-size:12px;letter-spacing:.04em;}}
</style>
<h1>아리랑마을 롤북 (영문)</h1>
<p>카드의 QR 은 이 주소를 거쳐 노션 게시본으로 넘어갑니다. 노션 링크가 바뀌어도 QR 은 그대로 씁니다.</p>
<ul>{rows}</ul>
""",
        encoding="utf-8",
    )
    (DOCS / ".nojekyll").write_text("")


def build_qr():
    OUT.mkdir(parents=True, exist_ok=True)
    for code in BOOKS:
        q = qrcode.QRCode(error_correction=ERROR_CORRECT_Q, box_size=BOX_SIZE, border=BORDER)
        q.add_data(f"{BASE}/r/{code}/")
        q.make(fit=True)
        q.make_image(
            fill_color=qr_ink(GROUPS[code]["color"]), back_color="white"
        ).save(OUT / f"{code}.png")


if __name__ == "__main__":
    build_pages()
    build_index()
    build_qr()
    for code, b in BOOKS.items():
        print(f"{code}  {BASE}/r/{code}/  ->  {target_url(code)}")
    print(f"\n리다이렉트 {DOCS/'r'}\nQR {OUT}")
