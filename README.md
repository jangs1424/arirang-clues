# 아리랑마을 단서카드 QR

소품에 붙인 QR을 스캔하면 해당 단서카드 이미지가 뜬다.

- 공개 주소: https://jangs1424.github.io/arirang-clues
- 카드 주소: `https://jangs1424.github.io/arirang-clues/c/P-1/` (36장, 코드는 `P-1` ~ `T-6`)

QR이 가리키는 주소는 고정이다. 이미지를 바꿔도 **인쇄한 QR은 다시 만들 필요가 없다.**

## 카드 이미지 수정

피그마에서 다시 받기:

```
export FIGMA_TOKEN=figd_xxx
python3 fetch_figma.py
python3 build.py
git add -A && git commit -m "카드 이미지 갱신" && git push
```

한 장만 직접 교체할 때는 `docs/cards/<코드>.png` 를 덮어쓰고 `python3 build.py` 후 push.
`build.py` 가 이미지 해시를 주소에 붙여주므로 폰에 옛 이미지가 남지 않는다.

## 카드 이름·색 수정

`cards.json` 을 고치고 `python3 build.py`.

## QR 인쇄

`build.py` 가 `qr/qr-sheet.pdf` 를 만든다. A4 2장, 한 장에 20개 (4열 × 5행).
칸마다 가구 색 테두리 + 가구명 띠 + 코드 + 한글명이 들어가서 소품에 맞춰 붙이기 쉽다.
낱장 QR은 `qr/<코드>.png`. `qr/` 는 git에 올리지 않으므로 `build.py` 를 돌리면 다시 생긴다.

QR 모듈 색은 가구 색을 그대로 쓰되, 흰 배경 대비가 7:1 이 안 되면 자동으로 어둡게 낮춘다
(`qr_ink()`). 주막(#CE981F)처럼 밝은 색은 스캔이 불안정해지기 때문이다.
그래서 주막·훈장은 테두리보다 QR이 어둡게 나온다 — 의도된 동작이다.

인쇄 전 `build.py` 로 PDF를 다시 만들었다면, 색을 바꾼 경우 스캔 검증을 한 번 돌려볼 것.
`cards.json` 의 색을 바꿔도 대비 보정이 자동으로 걸리지만, 실제 인쇄물로 한 장은 찍어보는 게 안전하다.
