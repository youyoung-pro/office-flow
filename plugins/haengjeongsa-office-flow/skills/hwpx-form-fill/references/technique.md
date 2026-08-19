# 전달문 — 법령 별지(hwp/hwpx) 서식을 원본 훼손 없이 편집·기입하는 기법

## 0. 목적
법제처·소관부처가 제공하는 법정 별지 서식(예: 자동차등록규칙 별지 제15호 자동차양도증명서)을
조항·테두리·서식을 전혀 바꾸지 않고, 빈칸에만 값을 채워 넣기 위한 표준 절차다.
Word 변환이나 재작성으로 서식이 흐트러지는 것을 막고, 법정 서식의 원형을 그대로 유지한다.

## 1. 핵심 원칙
1. 원본 hwpx의 구조 파일(header.xml, 조항 텍스트, 테두리, 셀 병합)은 절대 수정하지 않는다.
2. 오직 값이 들어갈 셀의 텍스트 노드에만 값을 덧붙인다.
3. hwp(구형 바이너리)는 직접 편집이 어렵다. hwpx(zip 기반 XML)로 받거나 변환한 뒤 편집한다.
4. 라벨 문자열(예: "성명(명칭)")로 셀을 찾지 않는다. 같은 라벨이 갑·을·공동명의자에 반복되므로
   반드시 셀 좌표(rowAddr, colAddr)로 대상 셀을 특정한다.

## 2. hwpx 구조 요점
hwpx는 zip 아카이브다. 주요 구성은 다음과 같다.
- `mimetype` : 값은 `application/hwp+zip`. zip에서 반드시 맨 앞, 무압축(-0)으로 저장돼야 한다.
- `Contents/section0.xml` : 실제 본문·표·텍스트. 편집 대상은 여기뿐이다.
- `Contents/header.xml` : 글꼴·문단·테두리 등 서식 선언. 건드리지 않는다.
- `Preview/PrvImage.png`, `Preview/PrvText.txt` : 미리보기 썸네일·텍스트. 레이아웃 파악에 유용.

표 구조 태그
- 셀: `<hp:tc> ... </hp:tc>`
- 셀 좌표: 셀 안의 `<hp:cellAddr colAddr="C" rowAddr="R"/>`
- 셀 병합: `<hp:cellSpan colSpan=".." rowSpan=".."/>`
- 텍스트: `<hp:t>내용</hp:t>` (한 셀에 여러 개일 수 있음)

많은 법정 서식은 "라벨과 값이 같은 셀"을 공유한다.
예: `성명(명칭)` 라벨 뒤 공백에 값을 적는 구조. 이때 값은 그 셀의 마지막 `<hp:t>` 뒤에 덧붙인다.
일부 서식은 라벨 셀과 값 셀이 분리돼 있으니, 아래 3단계에서 반드시 실제 구조를 먼저 확인한다.

## 3. 표준 절차

### 3-1. 압축 해제
```bash
cp 원본.hwpx form.hwpx
unzip -o -q form.hwpx -d unpacked
```

### 3-2. 레이아웃 파악 (반드시 먼저)
- `unpacked/Preview/PrvText.txt`를 읽어 라벨·항목 순서를 파악한다.
- `unpacked/Preview/PrvImage.png`를 이미지로 열어 "라벨 옆 빈칸" 방식인지 "값 셀 분리" 방식인지 확인한다.
- 아래 스크립트로 셀 좌표와 텍스트를 덤프해, 값을 넣을 셀의 (rowAddr, colAddr)를 확정한다.

```python
import re
xml = open('unpacked/Contents/section0.xml', encoding='utf-8').read()
for c in re.findall(r'<hp:tc\b.*?</hp:tc>', xml, re.S):
    m = re.search(r'colAddr="(\d+)" rowAddr="(\d+)"', c)
    if not m: continue
    txt = ' '.join(t.strip() for t in re.findall(r'<hp:t>(.*?)</hp:t>', c, re.S))
    print(f'row{m.group(2)} col{m.group(1)} :: {txt[:50]!r}')
```

### 3-3. 값 채우기 (마지막 텍스트 노드에 덧붙이기)
좌표로 대상 셀을 찾아, 그 셀의 마지막 `<hp:t>` 내용 뒤에 공백 + 값을 덧붙인다.
조항·테두리·다른 셀은 손대지 않는다.

```python
import re
path = 'unpacked/Contents/section0.xml'
xml = open(path, encoding='utf-8').read()

# (rowAddr, colAddr): 채울 값   ← 3-2에서 확정한 좌표 사용
targets = {
 (5, 2): "최종희",
 (5, 8): "660315-1000512",
 (7, 2): "서울특별시 성북구 돌곶이로40길 46, 708동 2103호",
 # ... 필요한 만큼
}

done = set()
for c in re.findall(r'<hp:tc\b.*?</hp:tc>', xml, re.S):
    m = re.search(r'colAddr="(\d+)" rowAddr="(\d+)"', c)
    if not m: continue
    key = (int(m.group(2)), int(m.group(1)))
    if key not in targets: continue
    tpos = list(re.finditer(r'<hp:t>(.*?)</hp:t>', c, re.S))
    assert tpos, f'텍스트 노드 없음 {key}'
    last = tpos[-1]
    newc = c[:last.start()] + '<hp:t>' + last.group(1) + '   ' + targets[key] + '</hp:t>' + c[last.end():]
    assert xml.count(c) == 1, f'셀이 유일하지 않음 {key}'   # 좌표 셀은 유일해야 함
    xml = xml.replace(c, newc)
    done.add(key)

missing = set(targets) - done
assert not missing, f'못 채운 항목: {missing}'
open(path, 'w', encoding='utf-8').write(xml)
print('채움 완료:', len(done))
```

주의: 빈 값 셀(텍스트 노드가 없는 셀)에 넣어야 하는 서식이라면, 마지막 `<hp:t>`가 없으므로
그 셀의 첫 문단(`<hp:p>`) 안 `<hp:run>`에 `<hp:t>값</hp:t>`을 삽입하는 방식으로 바꾼다.
이 경우에도 문단·런의 기존 속성(paraPrIDRef, charPrIDRef)은 유지한다.

### 3-4. 재패키징 (mimetype 규칙 필수)
```bash
cd unpacked
OUT="/경로/결과.hwpx"
rm -f "$OUT"
zip -X -0 "$OUT" mimetype        # mimetype을 맨 앞, 무압축으로
zip -X -rq "$OUT" . -x mimetype  # 나머지 전체
```

## 4. 검증 (hwpx는 이미지 렌더링이 안 되므로 텍스트·구조로 검증)
LibreOffice(soffice)는 hwpx를 열지 못한다. 따라서 다음으로 확인한다.
```python
import re, zipfile
import xml.dom.minidom as M
M.parse('unpacked/Contents/section0.xml')          # 1) XML 적합성
z = zipfile.ZipFile('결과.hwpx')
assert z.namelist()[0] == 'mimetype'               # 2) mimetype이 맨 앞
assert z.read('mimetype') == b'application/hwp+zip' # 3) mimetype 값
# 4) 채운 셀 값 재확인
xml = z.read('Contents/section0.xml').decode('utf-8')
for c in re.findall(r'<hp:tc\b.*?</hp:tc>', xml, re.S):
    m = re.search(r'colAddr="(\d+)" rowAddr="(\d+)"', c)
    if m and (int(m.group(2)), int(m.group(1))) in {(5,2),(5,8),(7,2)}:
        print(' '.join(t.strip() for t in re.findall(r'<hp:t>(.*?)</hp:t>', c, re.S)))
```
최종 확인은 한글(HWP)에서 파일을 한 번 열어 레이아웃을 눈으로 점검한다.

## 5. 함정 체크리스트
- mimetype을 압축(-0 아님)하거나 맨 앞이 아니면 한글이 파일을 인식하지 못한다.
- 라벨 문자열로 replace 하면 갑·을·공동명의자의 동일 라벨이 함께 바뀐다 → 반드시 좌표로 특정.
- `xml.count(c) == 1` 단언으로 대상 셀이 유일한지 확인한 뒤 replace 한다.
- header.xml·조항 텍스트·테두리·셀 병합은 수정 금지(원형 유지 원칙).
- Preview 썸네일은 편집 후 옛 이미지로 남지만, 한글에서 열면 본문이 재렌더되므로 무시해도 된다.
- 값은 라벨 셀의 서식(굵기 등)을 상속한다. 필요하면 별도 charPr 런을 추가하되 기존 속성은 보존.

## 6. 한 줄 요약
hwpx = zip(XML). `section0.xml`에서 셀 좌표(rowAddr, colAddr)로 대상 셀을 찾아 마지막
`<hp:t>` 뒤에 값만 덧붙이고, mimetype을 맨 앞·무압축으로 다시 압축한다. 조항·서식은 손대지 않는다.

## 7. 실전 기록 — 행정심판 서식 3종 (2026-08-03, 김경숙 과징금 불복)
원본 확보: law.go.kr/법령/행정심판법시행규칙, law.go.kr/법령/부동산실권리자명의등기에관한법률시행규칙
좌측 "서식" 트리에서 별지 제30호(행정심판 청구서)·제33호(집행정지신청서)·제39호(구술심리 신청서)·
제2호의2(과징금 납부기한연장·분할납부 신청서)의 .hwpx 링크 클릭 → 전부 hwp(OLE2)로 내려옴 →
Downloads의 UUID.tmp를 olefile PrvText로 식별 → 한글 2024(computer use)로 hwpx 변환.

채운 좌표(참고용, 판형 개정 시 재확인):
- 별지 30호: (5,1)성명 (6,1)주소 (7,1)주민번호 (8,1)전화 (13,1)피청구인 (16,1)처분내용 (17,1)안 날 (21,1)증거서류.
  치환: (14,1) "[  ] ○○시ㆍ도행정심판위원회"→"[√] 서울특별시행정심판위원회",
  (22,1) "<hp:fwSpace/>    [  ] 부"→"…[√] 부", (24,0) "  ○○행정심판위원회 "→"  서울특별시행정심판위원회 ".
- 별지 33호: (7,1)성명 (8,1)주소 (9,1)피신청인 (11,1)신청취지 (12,1)신청원인 (13,1)소명방법. 치환: (14,0) ○○위원회.
- 별지 2호의2: (5,5)성명 (5,12)생년월일 (6,5)주소 (7,5)전화 (13,5)발행번호 (14,5)부과금액 (15,5)납부기한
  (17,0)신청사유 (18,0)신청내용. 신청구분 [  ]연장/[  ]분납 체크는 결정 전이라 공란 유지.

셀 좌표 한정 치환 코드 요지: TC_RE로 셀 블록 순회 → cellAddr가 대상 좌표이고 아직 처리 전이면
그 블록 안에서만 str.replace(old, new, 1) → 재압축(mimetype STORED 선두).

## 8. 별지 분리 실전 기록 (2026-08-03 추가)
- 별지 33호 집행정지신청서: (12,1) 신청원인 → "[별지] 기재와 같음", 별지 1면 추가. 본문 charPr 14(돋움체 11pt) 클론+자간 -5, CENTER paraPr 38, LEFT paraPr 0 재사용.
- 별지 2호의2: (17,0) 신청사유·(18,0) 신청내용 → 별지 통합 1면. charPr 17 클론, CENTER 19, LEFT 1.
- 별지 30호 청구서: "청구 취지 및 청구 이유: 별지로 작성" → 별도 파일 대신 같은 hwpx 마지막에 별지 페이지로 통합(청구취지·청구이유·입증방법·관계법령·끝.). charPr 18 클론, CENTER 9, LEFT 0.
- 문단 삽입 위치: section0.xml의 </hs:sec> 직전. 첫 문단만 pageBreak="1".
- 검증: zip testzip, section0/header ET 파싱, mimetype 값, "[별 지]" 존재 확인.
