# -*- coding: utf-8 -*-
"""사무소 공통 정보 모듈. office_config.json 을 읽어 모든 생성기에 제공한다.
이 파일은 office-setup-wizard 가 배치하며, 값 수정은 office_config.json 에서만 한다."""
import json
from pathlib import Path

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "00_설정" / "office_config.json"

with open(_CONFIG_PATH, encoding="utf-8") as f:
    CONFIG = json.load(f)

OFFICE = CONFIG["office"]
PAYMENT = CONFIG["payment"]
NUMBERING = CONFIG["numbering"]

STANDARD_ROOT = Path(CONFIG["paths"]["standard_root"])
AUTOMATION = STANDARD_ROOT / "사무소_자동화"
TEMPLATES = AUTOMATION / "01_템플릿"
OUTPUT = AUTOMATION / "02_출력"
NUMBERING_DIR = AUTOMATION / "06_채번관리"
CASEWORK = STANDARD_ROOT / "PC문서함" / "01. 작업 문서함"

CHAEBEON_FILE = NUMBERING_DIR / "사무소_문서번호_채번부.txt"
LEDGER_FILE = NUMBERING_DIR / "사무소_문서등록대장.csv"
MAPPING_FILE = NUMBERING_DIR / "사건_폴더매핑.csv"

# 공식 산출물 표시 4종 (전자상거래법 제13조, 행정사법 제2조·제3조 근거)
LEGAL_IDS = {
    "행정사 자격번호": OFFICE["license_no"],
    "행정사업무신고번호": OFFICE["report_no"],
    "사업자등록번호": OFFICE["biz_reg_no"],
    "통신판매업 신고번호": OFFICE.get("ecommerce_no", ""),
}
