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

`qr/qr-sheet.html` 을 브라우저에서 열고 A4로 인쇄 (한 장에 4열, 코드·한글명 표기).
낱장 QR은 `qr/<코드>.png`. `qr/` 는 git에 올리지 않으므로 `build.py` 를 돌리면 다시 생긴다.
