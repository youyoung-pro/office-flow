#!/usr/bin/env python3
"""
hwpx_fill.py — 법령 별지 hwpx 서식을 원본 훼손 없이 채운다.

사용법:
  python hwpx_fill.py dump   원본.hwpx
  python hwpx_fill.py fill    원본.hwpx  결과.hwpx  fills.json
  python hwpx_fill.py verify  결과.hwpx  [--expect fills.json]

fills.json 형식: { "row,col": "값", ... }   (row/col 은 hp:cellAddr 의 rowAddr, colAddr)

원칙:
  - Contents/section*.xml 의 대상 셀 텍스트에만 값을 덧붙인다.
  - 대상 셀은 라벨이 아니라 (rowAddr, colAddr) 좌표로 특정한다.
  - mimetype 은 zip 맨 앞·무압축으로 다시 넣는다.
  - 조항/테두리/셀병합/header.xml 은 건드리지 않는다.
"""
import sys, re, json, zipfile, io
import xml.dom.minidom as minidom

TC_RE = re.compile(r'<hp:tc\b.*?</hp:tc>', re.S)
ADDR_RE = re.compile(r'colAddr="(\d+)" rowAddr="(\d+)"')
T_RE = re.compile(r'<hp:t>(.*?)</hp:t>', re.S)

SECTION_RE = re.compile(r'Contents/section\d+\.xml$')


def _sections(zf):
    return [n for n in zf.namelist() if SECTION_RE.search(n)]


def cmd_dump(hwpx):
    with zipfile.ZipFile(hwpx) as zf:
        for name in _sections(zf):
            xml = zf.read(name).decode('utf-8')
            print(f'=== {name} ===')
            for c in TC_RE.findall(xml):
                m = ADDR_RE.search(c)
                if not m:
                    continue
                txt = ' '.join(t.strip() for t in T_RE.findall(c))
                print(f'row{m.group(2)} col{m.group(1)} :: {txt[:60]!r}')


def _fill_cell(cell, value):
    """대상 셀 블록에 값을 덧붙인 새 블록을 돌려준다."""
    tpos = list(T_RE.finditer(cell))
    if tpos:  # 라벨/값 공유 셀: 마지막 텍스트 노드 뒤에 덧붙임
        last = tpos[-1]
        return cell[:last.start()] + '<hp:t>' + last.group(1) + '   ' + value + '</hp:t>' + cell[last.end():]
    # 텍스트 노드가 없는 빈 셀: 첫 run 안에 텍스트 노드 삽입, 없으면 첫 문단에 run 추가
    m = re.search(r'</hp:run>', cell)
    if m:
        return cell[:m.start()] + '<hp:t>' + value + '</hp:t>' + cell[m.start():]
    m = re.search(r'</hp:p>', cell)
    if m:
        return cell[:m.start()] + '<hp:run><hp:t>' + value + '</hp:t></hp:run>' + cell[m.start():]
    raise ValueError('셀에 문단/런이 없어 값을 넣을 위치를 찾지 못함')


def cmd_fill(src, out, fills_path):
    fills = json.load(open(fills_path, encoding='utf-8'))
    targets = {}
    for k, v in fills.items():
        r, c = k.replace(' ', '').split(',')
        targets[(int(r), int(c))] = str(v)

    with zipfile.ZipFile(src) as zf:
        names = zf.namelist()
        data = {n: zf.read(n) for n in names}
        infos = {n: zf.getinfo(n) for n in names}

    done = set()
    for name in [n for n in names if SECTION_RE.search(n)]:
        xml = data[name].decode('utf-8')
        for c in TC_RE.findall(xml):
            m = ADDR_RE.search(c)
            if not m:
                continue
            key = (int(m.group(2)), int(m.group(1)))
            if key not in targets or key in done:
                continue
            if xml.count(c) != 1:
                raise ValueError(f'셀 블록이 유일하지 않음: {key}')
            xml = xml.replace(c, _fill_cell(c, targets[key]))
            done.add(key)
        data[name] = xml.encode('utf-8')

    missing = set(targets) - done
    if missing:
        raise SystemExit(f'채우지 못한 좌표: {sorted(missing)} (dump 로 좌표 확인)')

    # mimetype 을 맨 앞·무압축으로, 나머지는 원래 순서대로 재압축
    with zipfile.ZipFile(out, 'w') as zf:
        if 'mimetype' in data:
            zi = zipfile.ZipInfo('mimetype')
            zi.compress_type = zipfile.ZIP_STORED
            zf.writestr(zi, data['mimetype'])
        for n in names:
            if n == 'mimetype':
                continue
            zi = zipfile.ZipInfo(n)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(zi, data[n])
    print(f'채움 완료: {len(done)}개 항목 -> {out}')


def cmd_verify(hwpx, expect_path=None):
    ok = True
    with zipfile.ZipFile(hwpx) as zf:
        names = zf.namelist()
        if names[0] != 'mimetype':
            print('  [실패] mimetype 이 zip 맨 앞이 아님'); ok = False
        else:
            print('  [통과] mimetype 이 맨 앞')
        if zf.read('mimetype') != b'application/hwp+zip':
            print('  [실패] mimetype 값이 application/hwp+zip 아님'); ok = False
        else:
            print('  [통과] mimetype 값 정상')
        for name in _sections(zf):
            try:
                minidom.parseString(zf.read(name))
                print(f'  [통과] XML 적합성: {name}')
            except Exception as e:
                print(f'  [실패] XML 오류 {name}: {e}'); ok = False
        if expect_path:
            fills = json.load(open(expect_path, encoding='utf-8'))
            want = {}
            for k, v in fills.items():
                r, c = k.replace(' ', '').split(',')
                want[(int(r), int(c))] = str(v)
            found = {}
            for name in _sections(zf):
                xml = zf.read(name).decode('utf-8')
                for c in TC_RE.findall(xml):
                    m = ADDR_RE.search(c)
                    if not m:
                        continue
                    key = (int(m.group(2)), int(m.group(1)))
                    if key in want:
                        found[key] = ' '.join(t.strip() for t in T_RE.findall(c))
            for key, val in want.items():
                txt = found.get(key, '')
                if val in txt:
                    print(f'  [통과] {key} 값 확인: {txt[:50]!r}')
                else:
                    print(f'  [실패] {key} 값 미확인 (기대 {val!r}, 실제 {txt[:50]!r})'); ok = False
    print('검증 결과:', '전체 통과' if ok else '실패 항목 있음')
    return ok


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__); return
    if a[0] == 'dump' and len(a) == 2:
        cmd_dump(a[1])
    elif a[0] == 'fill' and len(a) == 4:
        cmd_fill(a[1], a[2], a[3])
    elif a[0] == 'verify' and len(a) >= 2:
        exp = a[a.index('--expect') + 1] if '--expect' in a else None
        cmd_verify(a[1], exp)
    else:
        print(__doc__); raise SystemExit(2)


if __name__ == '__main__':
    main()
