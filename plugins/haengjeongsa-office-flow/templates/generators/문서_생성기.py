# -*- coding: utf-8 -*-
"""hwpx 서식 자리표시자 치환 발급기.
01_템플릿의 hwpx 서식에서 {{자리표시자}} 를 실제 값으로 바꿔 02_출력에 정본을 만든다.
pyhwpx 가 한컴 한글을 실제로 구동하므로 서식이 깨지지 않는다. 채번·등록대장 기록까지 한 번에 한다.

사용:
  python 문서_생성기.py <서식파일명> <값파일.json>
  python 문서_생성기.py --테스트          # 설치 검증용 (첫 서식으로 시험 발급)

값파일.json 예:
  {"문서종류": "견적서", "사건번호": "CS-01", "수신자": "홍길동", "업무명": "법인설립",
   "값": {"의뢰인명": "홍길동", "합계금액": "1,100,000"}}
문서번호는 자동 채번되어 {{문서번호}} 자리에 들어가고 값파일에 적지 않는다.
"""
import json
import sys
from datetime import datetime
from pyhwpx import Hwp
from 공통_사무소정보 import OFFICE, PAYMENT, TEMPLATES, OUTPUT
from 채번 import 다음_문서번호, 등록대장_기록

기본값 = {
    "사무소명": OFFICE["name_ko"],
    "대표행정사": OFFICE["representative"],
    "자격번호": OFFICE["license_no"],
    "업무신고번호": OFFICE["report_no"],
    "사업자등록번호": OFFICE["biz_reg_no"],
    "통신판매업신고번호": OFFICE.get("ecommerce_no", ""),
    "주소": OFFICE["address"],
    "전화": OFFICE["phone_mobile"],
    "유선전화": OFFICE["phone_office"],
    "팩스": OFFICE.get("fax", ""),
    "이메일": OFFICE["email"],
    "웹": OFFICE.get("web", ""),
    "입금계좌": f'{PAYMENT["bank"]} {PAYMENT["account"]} (예금주 {PAYMENT["holder"]})',
    "발급일": datetime.now().strftime("%Y년 %m월 %d일"),
}


def 발급(서식명, 스펙):
    서식 = TEMPLATES / 서식명
    if not 서식.exists():
        sys.exit(f"서식이 없습니다: {서식}")
    문서번호 = 다음_문서번호()
    값 = dict(기본값)
    값["문서번호"] = 문서번호
    값.update(스펙.get("값", {}))

    종류 = 스펙.get("문서종류", "문서")
    출력폴더 = OUTPUT / 종류
    출력폴더.mkdir(parents=True, exist_ok=True)
    출력파일 = 출력폴더 / f'{문서번호}_{스펙.get("수신자", "")}_{종류}.hwpx'

    hwp = Hwp(visible=False)
    try:
        hwp.open(str(서식))
        for k, v in 값.items():
            # 문서 전체에서 {{k}} 를 v 로 치환 (모든 표 칸 포함)
            hwp.replace_all(f"{{{{{k}}}}}", str(v))
        hwp.save_as(str(출력파일))
    finally:
        hwp.quit()

    등록대장_기록(문서번호, 스펙.get("사건번호", ""), 종류,
                스펙.get("수신자", ""), 스펙.get("업무명", ""), 출력파일)
    print(f"발급 완료: {문서번호} → {출력파일}")
    return 출력파일


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--테스트":
        서식들 = sorted(TEMPLATES.glob("*.hwpx"))
        if not 서식들:
            sys.exit("01_템플릿에 hwpx 서식이 없습니다. 서식을 먼저 준비하세요.")
        발급(서식들[0].name, {"문서종류": "테스트", "수신자": "설치검증",
                             "업무명": "설치 테스트", "값": {}})
    elif len(sys.argv) >= 3:
        with open(sys.argv[2], encoding="utf-8") as f:
            발급(sys.argv[1], json.load(f))
    else:
        sys.exit("사용법: python 문서_생성기.py <서식파일명> <값파일.json> | --테스트")
