#!/usr/bin/env python3
"""cards.json + docs/cards/*.png -> 뷰어 페이지 / QR 이미지 / 인쇄용 QR 시트."""

import hashlib
import html
import json
import pathlib
import shutil

import qrcode
from qrcode.constants import ERROR_CORRECT_Q

ROOT = pathlib.Path(__file__).parent
DOCS = ROOT / "docs"
IMG = DOCS / "cards"
QR = ROOT / "qr"

data = json.loads((ROOT / "cards.json").read_text(encoding="utf-8"))
BASE = data["baseUrl"].rstrip("/")
GROUPS = data["groups"]
CARDS = data["cards"]

for c in CARDS:
    c["group"] = c["code"].split("-")[0]
    c["url"] = f"{BASE}/c/{c['code']}/"
    src = IMG / f"{c['code']}.png"
    c["ready"] = src.exists()
    c["ver"] = hashlib.sha1(src.read_bytes()).hexdigest()[:8] if c["ready"] else "0"


VIEWER = """<!doctype html>
<html lang="ko">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=5">
<title>{title}</title>
<style>
  html,body{{margin:0;height:100%;background:#0b0b0c;}}
  body{{display:flex;align-items:center;justify-content:center;}}
  img{{max-width:100%;max-height:100%;display:block;}}
  p{{position:fixed;bottom:0;left:0;right:0;margin:0;padding:10px;
     text-align:center;font:12px/1.4 -apple-system,BlinkMacSystemFont,sans-serif;
     color:#555;}}
</style>
<img src="../../cards/{code}.png?v={ver}" alt="{title}">
<p>{code}</p>
"""

MISSING = """<!doctype html>
<html lang="ko">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
  html,body{{margin:0;height:100%;background:#0b0b0c;color:#888;
    display:flex;align-items:center;justify-content:center;
    font:15px/1.7 -apple-system,BlinkMacSystemFont,sans-serif;text-align:center;}}
</style>
<div>{code}<br>이미지 준비 중</div>
"""


def build_viewers():
    shutil.rmtree(DOCS / "c", ignore_errors=True)
    for c in CARDS:
        d = DOCS / "c" / c["code"]
        d.mkdir(parents=True, exist_ok=True)
        tpl = VIEWER if c["ready"] else MISSING
        title = html.escape(f"{c['code']} {c['kr']}")
        (d / "index.html").write_text(
            tpl.format(title=title, code=c["code"], ver=c["ver"]), encoding="utf-8"
        )
    (DOCS / ".nojekyll").write_text("")


def build_index():
    rows = []
    for g, meta in GROUPS.items():
        items = "".join(
            f'<li><a href="c/{c["code"]}/">{c["code"]}</a> {html.escape(c["kr"])}'
            f'{"" if c["ready"] else " <em>(이미지 없음)</em>"}</li>'
            for c in CARDS
            if c["group"] == g
        )
        rows.append(
            f'<section><h2 style="border-left:6px solid {meta["color"]}">'
            f'{html.escape(meta["kr"])}</h2><ul>{items}</ul></section>'
        )
    done = sum(c["ready"] for c in CARDS)
    (DOCS / "index.html").write_text(
        f"""<!doctype html>
<html lang="ko">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>아리랑마을 단서카드</title>
<style>
  body{{max-width:760px;margin:0 auto;padding:24px;
    font:15px/1.7 -apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo",sans-serif;color:#222;}}
  h1{{font-size:20px;}}
  h2{{font-size:15px;padding-left:10px;margin:28px 0 8px;}}
  ul{{list-style:none;padding:0;margin:0;
     display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:4px;}}
  a{{color:#0645ad;font-variant-numeric:tabular-nums;}}
  em{{color:#c00;font-style:normal;font-size:13px;}}
</style>
<h1>아리랑마을 단서카드 {done}/{len(CARDS)}</h1>
{"".join(rows)}
""",
        encoding="utf-8",
    )


def build_qr():
    QR.mkdir(exist_ok=True)
    for c in CARDS:
        q = qrcode.QRCode(error_correction=ERROR_CORRECT_Q, box_size=12, border=2)
        q.add_data(c["url"])
        q.make(fit=True)
        q.make_image(fill_color="black", back_color="white").save(QR / f"{c['code']}.png")

    cells = "".join(
        f'<div class="cell"><img src="{c["code"]}.png">'
        f'<b style="color:{GROUPS[c["group"]]["color"]}">{c["code"]}</b>'
        f'<span>{html.escape(c["kr"])}</span></div>'
        for c in CARDS
    )
    (QR / "qr-sheet.html").write_text(
        f"""<!doctype html>
<html lang="ko">
<meta charset="utf-8">
<title>단서카드 QR 스티커 시트</title>
<style>
  @page{{size:A4;margin:12mm;}}
  body{{margin:0;font:12px/1.4 -apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo",sans-serif;}}
  .grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:6mm;}}
  .cell{{border:1px dashed #bbb;border-radius:2mm;padding:3mm;text-align:center;
    break-inside:avoid;}}
  .cell img{{width:32mm;height:32mm;display:block;margin:0 auto 2mm;}}
  .cell b{{display:block;font-size:13px;letter-spacing:.05em;}}
  .cell span{{display:block;font-size:11px;color:#555;}}
</style>
<div class="grid">{cells}</div>
""",
        encoding="utf-8",
    )


if __name__ == "__main__":
    IMG.mkdir(parents=True, exist_ok=True)
    build_viewers()
    build_index()
    build_qr()
    ready = sum(c["ready"] for c in CARDS)
    print(f"카드 {len(CARDS)}장 / 이미지 {ready}장")
    print(f"뷰어 {DOCS/'c'}")
    print(f"QR   {QR}  (인쇄: qr-sheet.html)")
