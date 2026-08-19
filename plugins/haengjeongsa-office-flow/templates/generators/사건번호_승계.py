# -*- coding: utf-8 -*-
"""상담번호로 나간 견적서의 등록대장 행에 수임 확정된 사건번호를 소급 기입한다.
사용: python 사건번호_승계.py <상담번호> <사건번호>
예:  python 사건번호_승계.py "YY-07(상담)" CS-12
사람이 확인하며 실행하는 절차이므로 자동 실행하지 않는다."""
import csv
import sys
from 공통_사무소정보 import LEDGER_FILE


def 승계(상담번호, 사건번호):
    if not LEDGER_FILE.exists():
        sys.exit("등록대장이 없습니다.")
    with open(LEDGER_FILE, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    바뀐 = 0
    for row in rows[1:]:
        if len(row) >= 2 and row[1] == 상담번호:
            row[1] = 사건번호
            바뀐 += 1
    if not 바뀐:
        sys.exit(f"상담번호 {상담번호} 행이 등록대장에 없습니다.")
    with open(LEDGER_FILE, "w", newline="", encoding="utf-8-sig") as f:
        csv.writer(f, lineterminator="\r\n").writerows(rows)
    print(f"승계 완료: {상담번호} → {사건번호} ({바뀐}건)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("사용법: python 사건번호_승계.py <상담번호> <사건번호>")
    승계(sys.argv[1], sys.argv[2])
