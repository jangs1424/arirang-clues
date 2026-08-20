#!/usr/bin/env python3
"""spares.json -> 예비 QR 페이지 / 인쇄용 무지 스티커 시트.

인쇄한 QR 의 링크가 잘못됐거나 스티커가 훼손됐을 때 그 위에 덧붙이는 예비 스티커.
QR 이 가리키는 주소(/s/<번호>/)는 고정이고, 그 번호가 어디로 갈지는 spares.json 이 정한다.
값을 고쳐 다시 돌리면 **이미 붙인 스티커는 그대로 두고** 목적지만 바뀐다.

집 색·이름을 넣지 않는 이유: 어느 가구 카드에든 덧붙일 수 있어야 하기 때문이다.
"""

import html
import json
import pathlib

import qrcode
from qrcode.constants import ERROR_CORRECT_Q

from build import BASE, CARDS, COL_W, COLS, GAP, MARGIN, QR_MM, ROW_H, VIEWER, DOCS, QR, print_pdf

ROOT = pathlib.Path(__file__).parent
INK = "#111111"  # 무지 스티커라 집 색을 안 쓴다. 검정이 대비가 가장 안전하다.

BY_CODE = {c["code"]: c for c in CARDS}

data = json.loads((ROOT / "spares.json").read_text(encoding="utf-8"))
SPARES = data["spares"]

PENDING = """<!doctype html>
<html lang="ko">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>준비 중</title>
<style>
  html,body{{margin:0;height:100%;background:#0b0b0c;color:#888;
    display:flex;align-items:center;justify-content:center;text-align:center;
    font:15px/1.9 -apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo",sans-serif;}}
  b{{display:block;color:#ddd;font-size:13px;letter-spacing:.1em;margin-bottom:8px;}}
</style>
<div>
  <b>S{n}</b>
  준비 중입니다.<br>진행요원에게 문의해 주세요.
</div>
"""

REDIRECT = """<!doctype html>
<html lang="ko">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<link rel="canonical" href="{target}">
<meta http-equiv="refresh" content="0;url={target}">
<title>이동 중</title>
<style>
  html,body{{margin:0;height:100%;background:#0b0b0c;color:#888;
    display:flex;align-items:center;justify-content:center;text-align:center;
    font:14px/1.8 -apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo",sans-serif;}}
  a{{color:#9ab;}}
</style>
<script>location.replace("{target}");</script>
<a href="{target}">열기</a>
"""


def resolve(n, value):
    """spares.json 값 -> (페이지 HTML, 사람이 읽을 목적지 설명)."""
    v = value.strip()
    if not v:
        return PENDING.format(n=n), "— (미지정)"
    if v.startswith(("http://", "https://")):
        return REDIRECT.format(target=html.escape(v, quote=True)), v
    if v in BY_CODE:
        c = BY_CODE[v]
        return (
            VIEWER.format(
                title=html.escape(f"{c['code']} {c['kr']}"), code=c["code"], ver=c["ver"]
            ),
            f"{c['code']} {c['kr']}",
        )
    raise SystemExit(
        f"spares.json '{n}' 값이 잘못됐습니다: {v!r}\n"
        f"카드 코드(예: P-3) 나 http 로 시작하는 전체 주소만 넣을 수 있습니다."
    )


def build_pages():
    # 오타 하나로 일부만 반영된 채 멈추면 현장에서 상태를 알기 어렵다. 전부 검사한 뒤에 쓴다.
    built = [(n, *resolve(n, v)) for n, v in SPARES.items()]
    for n, page, _ in built:
        d = DOCS / "s" / n
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(page, encoding="utf-8")
    return [(n, desc) for n, _, desc in built]


def build_sheet():
    QR.mkdir(exist_ok=True)
    sp = QR / "spare"
    sp.mkdir(exist_ok=True)
    for n in SPARES:
        # 정본 시트와 같은 조건(border=1 + 칸 안쪽 흰 여백)으로 맞춘다.
        q = qrcode.QRCode(error_correction=ERROR_CORRECT_Q, box_size=12, border=1)
        q.add_data(f"{BASE}/s/{n}/")
        q.make(fit=True)
        q.make_image(fill_color=INK, back_color="white").save(sp / f"{n}.png")

    cells = "".join(
        f'<div class="cell"><img src="spare/{n}.png"><b>S{n}</b></div>' for n in SPARES
    )
    (QR / "qr-spare.html").write_text(
        f"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<title>Spare QR Stickers</title>
<style>
  @page{{size:A4;margin:{MARGIN}mm;}}
  body{{margin:0;font:12px/1.15 -apple-system,BlinkMacSystemFont,Helvetica,sans-serif;
    -webkit-print-color-adjust:exact;print-color-adjust:exact;}}
  .grid{{display:grid;grid-template-columns:repeat({COLS},{COL_W}mm);justify-content:center;
    grid-auto-rows:{ROW_H:.2f}mm;gap:{GAP}mm;}}
  .cell{{border:0.5mm solid #111;overflow:hidden;text-align:center;
    break-inside:avoid;padding-bottom:0.8mm;}}
  .cell img{{height:{QR_MM}mm;width:auto;max-width:100%;display:block;margin:0.8mm auto 0;}}
  .cell b{{display:block;font-size:15px;line-height:1.1;color:#111;
    font-variant-numeric:tabular-nums;padding-top:0.5mm;}}
</style>
<div class="grid">{cells}</div>
""",
        encoding="utf-8",
    )


if __name__ == "__main__":
    rows = build_pages()
    build_sheet()
    print_pdf("qr-spare")
    for n, desc in rows:
        print(f"S{n}  {BASE}/s/{n}/  ->  {desc}")
    print(f"\n예비 {len(rows)}장")
    print(f"페이지 {DOCS/'s'}")
    print(f"QR     {QR}  (인쇄: qr-spare.pdf)")
