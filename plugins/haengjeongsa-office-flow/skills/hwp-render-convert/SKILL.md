---
name: hwp-render-convert
description: >-
  한컴 한글 없이 클라우드에서 hwp/hwpx/hml 문서를 처리하는 행정사사무소 보조 도구.
  두 용도로 쓴다. 첫째, hwp로만 내려온 서식을 hwpx로 변환한다(hwp→hwpx, 대표 PC 한글 의존 제거).
  둘째, 채워 넣은 서식이나 원본을 PDF·PNG로 렌더링해 보고·검수용 미리보기를 만든다.
  "hwp를 hwpx로 변환", "한글 없이 변환", "hwp 변환", "서식 PDF로 렌더링", "검수용 미리보기",
  "hwpx 미리보기 만들어줘", "hwp 열어서 PDF로", "hwp→hwpx"라고 하거나, hwpx-form-fill 작업 중
  hwp 원본을 hwpx로 바꾸거나 작성 결과를 눈으로 검수해야 할 때 사용한다. 오픈소스 rhwp(@rhwp/core,
  MIT)를 사용하며, 최종 관공서 제출본의 형식 적합성은 반드시 한글 확인 산출물을 기준으로 삼는다.
---

# hwp-render-convert

한컴 오피스 없이 클라우드 환경에서 아래한글 문서(hwp 바이너리·hwpx·hml)를 변환·렌더링한다.
오픈소스 rhwp의 WASM 엔진(@rhwp/core, MIT)을 사용한다.

## 정식 편입 범위 (두 용도만)

1. hwp→hwpx 변환기. 지금까지 hwp로만 내려오는 서식은 대표 PC 한글로 변환했다. 이 스킬로 클라우드에서 한글 없이 변환해 대표 PC 의존과 세션 왕복을 줄인다.
2. 렌더링 검수 도구. 채워 넣은 서식이나 원본을 PDF·PNG로 렌더링해 한글을 열지 않고 보고용 미리보기 한 장을 남긴다.

서식 채우기 본작업의 대체재가 아니다. 법정 별지 서식에 값을 채우는 정밀 작업은 기존 hwpx-form-fill 스킬(셀 좌표 기반 XML 편집)을 그대로 쓴다.

## 절대 원칙

관공서 최종 제출본의 형식 적합성은 반드시 한컴 한글로 연 산출물을 기준으로 확정한다. 이 스킬의 렌더링은 검수·미리보기 보조이며, 렌더링 시 한글 기본 글꼴(함초롬 계열)이 Noto CJK로 대체 표시될 수 있다. 이 대체는 화면 표시에만 적용되고 변환된 hwpx 파일 자체의 글꼴 지정에는 영향을 주지 않는다.

## 사용 절차

작업 폴더에서 스크립트를 실행한다. 사건 파일이 대표 PC(문서함)에 있으면 device_stage_files로 스테이징한 뒤 처리하고, 결과물은 SendUserFile로 전달하며 필요 시 device_commit_files로 문서함에 되돌린다.

1. 환경 준비(최초 1회 또는 새 세션): `bash scripts/setup.sh`
2. hwp→hwpx 변환: `node scripts/convert.mjs <입력.hwp> [출력.hwpx]`
   - 형식 지정: `--to hwpx|hwp|hml` (기본 hwpx)
   - 출력에 변환본을 다시 로드한 페이지 수(reloadPages)를 함께 보고해 자체 검증한다.
3. PDF/PNG 렌더링(검수용): `node scripts/render.mjs <입력.hwp|hwpx> [출력.pdf] [--png <폴더>] [--scale 1.5]`
   - PDF는 페이지 크기를 원본 그대로 맞춘다. `--png`를 주면 페이지별 PNG도 만든다.

## hwpx-form-fill 연계

hwpx-form-fill 작업 시 이 스킬을 다음 두 지점에서 호출한다. 서식 원본이 hwp로만 있을 때 먼저 convert.mjs로 hwpx를 만들어 채우기에 넘기고, 채우기를 마친 hwpx는 render.mjs로 PDF를 만들어 대표행정사 검수·보고에 쓴다.

## 파일 구성

scripts/lib.mjs 는 @rhwp/core와 playwright를 로컬·전역 무관하게 로드하는 공용 모듈이다. convert.mjs·render.mjs 는 이를 사용한다. setup.sh 는 의존성(@rhwp/core, playwright/chromium, 한국어 폰트)을 점검·설치한다.

## 검증 이력

2026-08-06 파일럿에서 실제 서식으로 확인함. 정보공개 청구서 별지 서식(hwp)을 병합셀·음영·체크박스·직인란·유의사항·용지규격 각주까지 원형 보존하며 렌더링했고, hwp→hwpx 변환본은 원본과 픽셀 단위로 동일하게 재현되어 렌더링 수준 무손실을 확인했다. hwpx 다중 페이지 문서도 정상 렌더링했다.
