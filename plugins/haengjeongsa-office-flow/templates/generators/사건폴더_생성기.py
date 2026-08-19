# -*- coding: utf-8 -*-
"""사건 폴더 생성기. 사건번호로 표준 사건 폴더와 하위 여덟 칸을 만들고 매핑에 등재한다.
사용: python 사건폴더_생성기.py <사건번호> <의뢰인명> <사건명> [업무분류폴더명]
매핑에 이미 있는 사건번호는 중복 생성하지 않는다."""
import csv
import sys
from datetime import datetime
from 공통_사무소정보 import CASEWORK, MAPPING_FILE, TEMPLATES

하위칸 = ["00. 첨부(증거자료)_최종", "10. 사무소_작업문서", "20. 별건",
        "30. 원본_등기·판결·법원", "40. 원본_계약·취득", "90. 참고·서식·판독",
        "99. 수집원본(출처별_정리전)", "_이전버전"]

MAPPING_COLUMNS = ["사건번호", "폴더경로", "등록일시", "생성방식", "비고"]


def 이미_있는가(사건번호):
    if not MAPPING_FILE.exists():
        return None
    with open(MAPPING_FILE, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("사건번호") == 사건번호:
                return row.get("폴더경로")
    return None


def 생성(사건번호, 의뢰인, 사건명, 분류폴더=None):
    기존 = 이미_있는가(사건번호)
    if 기존:
        print(f"이미 등재된 사건입니다: {사건번호} → {기존}")
        return 기존

    상위 = CASEWORK / 분류폴더 if 분류폴더 else CASEWORK
    사건폴더 = 상위 / f"{사건번호}_{의뢰인}_{사건명}"
    사건폴더.mkdir(parents=True, exist_ok=True)
    for 칸 in 하위칸:
        (사건폴더 / 칸).mkdir(exist_ok=True)

    지침 = TEMPLATES / "사건프로젝트_표준지침.md"
    대상 = 사건폴더 / "00_사무소지침.md"
    if 지침.exists() and not 대상.exists():
        대상.write_text(지침.read_text(encoding="utf-8"), encoding="utf-8")

    개요 = 사건폴더 / "00_사건개요.md"
    if not 개요.exists():
        개요.write_text(
            f"# 사건개요 {사건번호}\n\n사건번호: {사건번호}\n사건명: {사건명}\n"
            f"의뢰인: {의뢰인}\n등록일: {datetime.now():%Y-%m-%d}\n"
            f"사건 폴더: {사건폴더}\n\n공통 규약은 00_사무소지침.md 참조.\n\n## 진행 기록\n\n",
            encoding="utf-8")

    new = not MAPPING_FILE.exists()
    with open(MAPPING_FILE, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, lineterminator="\r\n")
        if new:
            w.writerow(MAPPING_COLUMNS)
        w.writerow([사건번호, str(사건폴더), datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "생성기", ""])
    print(f"사건 폴더 생성: {사건폴더}")
    return 사건폴더


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit("사용법: python 사건폴더_생성기.py <사건번호> <의뢰인명> <사건명> [업무분류폴더명]")
    생성(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
