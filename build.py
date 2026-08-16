#!/usr/bin/env python3
"""cards.json + docs/cards/*.png -> 뷰어 페이지 / QR 이미지 / 인쇄용 QR 시트."""

import hashlib
import html
import json
import pathlib
import shutil
import subprocess

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


def _luminance(rgb):
    """WCAG 상대 휘도."""
    out = []
    for v in rgb:
        c = v / 255
        out.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * out[0] + 0.7152 * out[1] + 0.0722 * out[2]


def qr_ink(hexcolor, min_contrast=7.0):
    """가구 색을 QR 모듈에 쓸 만큼 어둡게 낮춘다.

    흰 배경 대비가 모자라면 스캔이 불안정해진다. 노란색 계열(주막 #CE981F)이
    특히 위험해서, 대비 7:1 을 넘길 때까지 단계적으로 어둡게 만든다.
    """
    rgb = [int(hexcolor[i : i + 2], 16) for i in (1, 3, 5)]
    for _ in range(60):
        if 1.05 / (_luminance(rgb) + 0.05) >= min_contrast:
            break
        rgb = [max(0, int(v * 0.94)) for v in rgb]
    return "#%02X%02X%02X" % tuple(rgb)


def build_qr():
    QR.mkdir(exist_ok=True)
    ink = {g: qr_ink(m["color"]) for g, m in GROUPS.items()}
    for c in CARDS:
        # border=1: QR 자체 여백을 최소로. 나머지 quiet zone 은 칸 안쪽 흰 여백이 맡는다.
        q = qrcode.QRCode(error_correction=ERROR_CORRECT_Q, box_size=12, border=1)
        q.add_data(c["url"])
        q.make(fit=True)
        q.make_image(fill_color=ink[c["group"]], back_color="white").save(
            QR / f"{c['code']}.png"
        )

    css = "".join(f'.{g}{{--c:{m["color"]}}}' for g, m in GROUPS.items())
    cells = "".join(
        f'<div class="cell {c["group"]}">'
        f'<div class="band">{html.escape(GROUPS[c["group"]]["en"])}</div>'
        f'<img src="{c["code"]}.png">'
        f'<b>{c["code"]}</b><span>{html.escape(c["en"])}</span></div>'
        for c in CARDS
    )
    # 5열 × 4행 = 20구/장, A4 2장. QR 이 칸을 거의 꽉 채우게 둔다.
    (QR / "qr-sheet.html").write_text(
        f"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<title>Clue Card QR Stickers</title>
<style>
  @page{{size:A4;margin:7mm;}}
  body{{margin:0;font:12px/1.15 -apple-system,BlinkMacSystemFont,Helvetica,sans-serif;
    -webkit-print-color-adjust:exact;print-color-adjust:exact;}}
  .grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:2mm;}}
  .cell{{border:0.6mm solid var(--c);border-radius:1.5mm;overflow:hidden;text-align:center;
    break-inside:avoid;padding-bottom:1.2mm;}}
  .band{{background:var(--c);color:#fff;font-size:6.4px;letter-spacing:.04em;
    padding:1mm 0;white-space:nowrap;}}
  .cell img{{width:100%;display:block;padding:1.2mm;box-sizing:border-box;}}
  .cell b{{display:block;font-size:11px;letter-spacing:.06em;color:var(--c);
    font-variant-numeric:tabular-nums;}}
  .cell span{{display:block;font-size:7.2px;line-height:1.25;color:#444;
    letter-spacing:.02em;padding:0.4mm 1mm 0;}}
  {css}
</style>
<div class="grid">{cells}</div>
""",
        encoding="utf-8",
    )


CHROME = pathlib.Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")


def print_qr_sheet():
    if not CHROME.exists():
        print("Chrome 없음 - qr-sheet.html 을 직접 인쇄하세요.")
        return
    subprocess.run(
        [
            str(CHROME),
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={QR / 'qr-sheet.pdf'}",
            (QR / "qr-sheet.html").as_uri(),
        ],
        check=True,
        capture_output=True,
    )


if __name__ == "__main__":
    IMG.mkdir(parents=True, exist_ok=True)
    build_viewers()
    build_index()
    build_qr()
    print_qr_sheet()
    ready = sum(c["ready"] for c in CARDS)
    print(f"카드 {len(CARDS)}장 / 이미지 {ready}장")
    print(f"뷰어 {DOCS/'c'}")
    print(f"QR   {QR}  (인쇄: qr-sheet.html)")
