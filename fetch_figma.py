#!/usr/bin/env python3
"""피그마에서 단서카드 36장을 고해상도 PNG로 내려받아 docs/cards/ 에 저장.

  export FIGMA_TOKEN=figd_xxx
  python3 fetch_figma.py          # 내려받기
  python3 fetch_figma.py --tree   # 노드 이름만 확인
"""

import json
import os
import pathlib
import re
import sys

import requests

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "docs" / "cards"
MANIFEST = ROOT / "cards.json"
CFG = json.loads(MANIFEST.read_text(encoding="utf-8"))["figma"]

TOKEN = os.environ.get("FIGMA_TOKEN")
if not TOKEN:
    sys.exit("FIGMA_TOKEN 환경변수가 없습니다.")

API = "https://api.figma.com/v1"
HEAD = {"X-Figma-Token": TOKEN}
CODE = re.compile(r"\b([PMAGIT])[-_ ]?([1-6])\b", re.I)


def get(path, timeout=120, **params):
    r = requests.get(f"{API}/{path}", headers=HEAD, params=params, timeout=timeout)
    r.raise_for_status()
    return r.json()


def walk(node, depth=0):
    yield depth, node
    for child in node.get("children", []):
        yield from walk(child, depth + 1)


def check_names(names):
    """피그마 프레임 이름과 cards.json 의 한글명이 어긋나면 알린다 (QR 시트 라벨용)."""
    for card in json.loads(MANIFEST.read_text(encoding="utf-8"))["cards"]:
        figma = names.get(card["code"])
        if figma and figma != card["kr"]:
            print(f"  ! {card['code']} 이름 불일치 - 피그마 '{figma}' / cards.json '{card['kr']}'")


def main():
    doc = get(f"files/{CFG['fileKey']}/nodes", ids=CFG["nodeId"], depth=3)
    root = doc["nodes"][CFG["nodeId"]]["document"]

    if "--tree" in sys.argv:
        for d, n in walk(root):
            print(f"{'  ' * d}{n['id']}  [{n['type']}]  {n['name']}")
        return

    found = {}
    for _, n in walk(root):
        m = CODE.search(n["name"])
        if m and n["type"] in ("FRAME", "COMPONENT", "INSTANCE", "GROUP"):
            code = f"{m.group(1).upper()}-{m.group(2)}"
            found.setdefault(code, (n["id"], n["name"][m.end() :].strip(" ]·-")))

    if len(found) != 36:
        print(f"카드 {len(found)}개만 인식됨. --tree 로 노드 이름 확인 필요.")
        print(sorted(found))
        if not found:
            return

    check_names({c: name for c, (_, name) in found.items()})
    # 36장을 한 번에 렌더 요청하면 피그마 쪽에서 타임아웃 난다. 6장씩 끊어서 요청.
    ids = [nid for nid, _ in found.values()]
    urls = {}
    for i in range(0, len(ids), 6):
        chunk = ids[i : i + 6]
        urls.update(
            get(
                f"images/{CFG['fileKey']}",
                ids=",".join(chunk),
                format="png",
                scale=CFG["scale"],
            )["images"]
        )
        print(f"  렌더 {min(i + 6, len(ids))}/{len(ids)}")

    OUT.mkdir(parents=True, exist_ok=True)
    for code, (nid, _) in sorted(found.items()):
        url = urls.get(nid)
        if not url:
            print(f"  {code} 실패 (렌더 URL 없음)")
            continue
        (OUT / f"{code}.png").write_bytes(requests.get(url, timeout=120).content)
        print(f"  {code} ok")

    print(f"{len(found)}장 저장 -> {OUT}")


if __name__ == "__main__":
    main()
