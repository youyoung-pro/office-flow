# -*- coding: utf-8 -*-
"""문서번호 채번과 등록대장 기록. 채번부 파일이 유일 기준이며 번호를 코드에 적지 않는다."""
import csv
from datetime import datetime
from 공통_사무소정보 import NUMBERING, CHAEBEON_FILE, LEDGER_FILE

LEDGER_COLUMNS = ["문서번호", "사건번호", "발급일시", "문서종류", "수신자", "업무명", "파일경로"]


def 다음_문서번호():
    """채번부를 읽어 다음 문서번호를 발급하고 채번부를 갱신한다."""
    year = datetime.now().year
    cur_year, seq = year, 1
    if CHAEBEON_FILE.exists():
        parts = CHAEBEON_FILE.read_text(encoding="utf-8-sig").split()
        if len(parts) >= 2:
            cur_year, seq = int(parts[0]), int(parts[1])
    if cur_year != year:  # 해가 바뀌면 번호를 되돌린다
        cur_year, seq = year, 1
    doc_no = NUMBERING["doc_number_format"].format(
        doc_prefix=NUMBERING["doc_prefix"], year=cur_year, seq=seq)
    CHAEBEON_FILE.write_text(f"{cur_year} {seq + 1}\n", encoding="utf-8-sig")
    return doc_no


def 등록대장_기록(문서번호, 사건번호, 문서종류, 수신자, 업무명, 파일경로):
    """등록대장 CSV(UTF-8 BOM, CRLF)에 한 행을 추가한다."""
    new = not LEDGER_FILE.exists()
    with open(LEDGER_FILE, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, lineterminator="\r\n")
        if new:
            w.writerow(LEDGER_COLUMNS)
        w.writerow([문서번호, 사건번호, datetime.now().strftime("%Y-%m-%d %H:%M"),
                    문서종류, 수신자, 업무명, str(파일경로)])
