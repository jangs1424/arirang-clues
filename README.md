# 아리랑마을 단서카드 QR

소품에 붙인 QR을 스캔하면 해당 단서카드 이미지가 뜬다.

- 공개 주소: https://jangs1424.github.io/arirang-clues
- 카드 주소: `https://jangs1424.github.io/arirang-clues/c/P-1/` (36장, 코드는 `P-1` ~ `T-6`)

QR이 가리키는 주소는 고정이다. 이미지를 바꿔도 **인쇄한 QR은 다시 만들 필요가 없다.**

## 롤북 QR (영문, 6가구)

캐릭터 카드 앞면 "Your story" 아래 QR. 스캔하면 노션에 게시한 **영문 롤북**이 열린다.

- 롤북 주소: `https://jangs1424.github.io/arirang-clues/r/P/` (코드는 `P M A G I T` — 단서카드 그룹코드와 동일)
- 목록: `https://jangs1424.github.io/arirang-clues/r/`

```
python3 build_rolebooks.py
git add -A && git commit -m "롤북 QR 갱신" && git push
```

**노션 링크가 바뀌면 `rolebooks.json` 의 `notion` 값(페이지 ID)만 고치고 다시 돌린다.**
QR 이 가리키는 주소는 깃허브 쪽이라 고정이므로 **인쇄한 카드는 그대로 쓴다.**
게시 주소는 슬러그 없이 페이지 ID 만 붙인 형태(`.../<ID>`)를 쓴다 — 노션이 제목 슬러그로
리다이렉트해 주기 때문에 롤북 제목을 고쳐도 주소가 깨지지 않는다.

색은 `cards.json` 의 `groups` 를 그대로 쓴다(팔레트 단일 출처). 단서카드와 같은 대비 보정
(`qr_ink()`)이 걸리므로 주막(노랑)·훈장은 QR 이 가구색보다 어둡게 나온다 — 의도된 동작이다.

카드에 얹는 PNG 는 `qr/rolebook/<코드>.png`. `border=2` 로 quiet zone 을 이미지 안에 넣었다 —
카드 배경이 어두워서 흰 여백이 이미지 밖에 있으면 스캔이 불안정해진다. 이 여백을 잘라내지 말 것.

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

`build.py` 가 `qr/qr-sheet.pdf` 를 만든다. A4 3장, 한 장에 30개 (5열 × 6행). 라벨은 영문.
칸에는 **집 이름 띠(POSTMAN · PARK)와 번호만** 들어간다. 항목명은 일부러 뺐다 —
종이에 박히면 나중에 못 고치기 때문. 대신 `qr/qr-list.pdf` (배치표) 를 같이 뽑아서 대조한다.
띠 문구는 `cards.json` 의 `groups[*].sticker` 에서 고친다.
스티커 한 칸은 35 × 45.9mm, QR 자체는 31mm. 낱장 QR은 `qr/<코드>.png`.
`qr/` 는 git에 올리지 않으므로 `build.py` 를 돌리면 다시 생긴다.

**36장이 두 벌 들어간다 (원본 + 여벌).** 36은 5열로 안 떨어져서 첫 벌 마지막 줄에
T-6 하나만 남는다. 그 줄의 남은 4칸은 일부러 비우고 `SPARE SET ↓` 만 찍는다.
여벌은 그 다음 줄부터 시작하므로, 인쇄물에서 어디부터가 여벌인지 눈으로 바로 갈린다.
이 빈칸을 메우면 경계가 사라지니 채우지 말 것.

## 배치표

`qr/qr-list.pdf` — A4 1장. 집별로 1~6번이 무슨 단서인지 국영문으로 적혀 있다.
스티커에 항목명이 없으므로 소품에 붙일 때는 이 표가 있어야 한다.

레이아웃 숫자(`MARGIN`/`GAP`/`COLS`/`ROWS`/`QR_MM`/`COL_W`)는 `build.py` 맨 위에 모여 있다.
`ROW_H` 는 A4 세로에 6행이 떨어지게 계산한 값이고 0.4mm 여유가 들어가 있다.
`QR_MM` 을 키우면 행 높이를 넘겨서 6행째가 다음 장으로 밀린다 — 둘은 같이 봐야 한다.

QR 이미지의 quiet zone 은 1모듈까지만 넣고(`border=1`), 나머지 여백은 칸 안쪽 흰 패딩이 맡는다.
이걸 0으로 더 줄이면 스캔이 불안정해지므로 건드리지 말 것.

QR 모듈 색은 가구 색을 그대로 쓰되, 흰 배경 대비가 7:1 이 안 되면 자동으로 어둡게 낮춘다
(`qr_ink()`). 주막(#CE981F)처럼 밝은 색은 스캔이 불안정해지기 때문이다.
그래서 주막·훈장은 테두리보다 QR이 어둡게 나온다 — 의도된 동작이다.

현재 PDF는 300/150/100/72dpi, 컬러·흑백 모두에서 72개 전부 디코드된다(고유 36종).
인쇄 전 `build.py` 로 PDF를 다시 만들었다면, 색을 바꾼 경우 스캔 검증을 한 번 돌려볼 것.
`cards.json` 의 색을 바꿔도 대비 보정이 자동으로 걸리지만, 실제 인쇄물로 한 장은 찍어보는 게 안전하다.
